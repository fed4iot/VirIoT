from eve import Eve
from eve.methods.post import post_internal
import json

def remove_secret_fields(resource, response):
    del(response['_etag'])
    del(response['_created'])
    del(response['_updated'])
    # remove @context if it exists
    response.pop("@context", None)
    del(response['_id'])

def remove_secret_fields_in_list(resource, response):
    for item in response['_items']:
        remove_secret_fields(resource, item)




def materialize_latestentities_via_aggregation(resource_name, items):
    app.data.driver.db.entities.aggregate(latestentities_pipeline)

# we group by NGSI-LD "id", hence it has to be assigned to the _id pivot of the group.
# $$ROOT to keep the whole document per each name followed by $replaceRoot to promote the document to the top.
# https://stackoverflow.com/questions/52566913/how-to-group-in-mongodb-and-return-all-fields-in-result
latestentities_pipeline = [
    # oldest first, normal direction sorting
    {"$sort" : {"_created":1}},
    # group them based on the same NGSI-LD id.
    # then, either pick fields from first, so that basically id will always
    # stay the same (the ObjectID of the first inserted item), hence
    # the merge will overwrite the ones with same id,
    # OR let the merge create new ObjectIds everytime and use the "parkingsite" NGSI-LD id
    # as reference for voerwriting during the merge.
    # I prefer the second option, so that _Created and _updated are the ones from the last
    # individual.    
    {"$group" : {"_id":"$id", "doc":{"$last":"$$ROOT"}}},
    {"$replaceRoot":{"newRoot":"$doc"}},
    {"$project":{"_id":0}},
    {"$set":{"_id":"$id"}},
    {"$unset":["_etag"]},
    {"$merge":"latestentities"},
]




def push_systemvthings_locally(request, payload):
    x = post_internal('vthingsendpoint', json.loads(payload.get_data()).get('_items'))
    print(x)
    #response_dict = json.loads(payload.get_data())
    #for key, value in sorted(response_dict.items()):
    #    print("KK "+key)
    #    print("{} : {}".format(key, value))




app = Eve()

app.on_fetched_item += remove_secret_fields
app.on_fetched_resource += remove_secret_fields_in_list

# we now want to trigger the aggegation that creates the "materialized view" named
# latestentities, AFTER each time items are inserted, updated, replaced, deleted into the entities collection
# well, btter to trigger on any insert, etc.. since we have multiple POST entry points
app.on_inserted += materialize_latestentities_via_aggregation
app.on_replaced += materialize_latestentities_via_aggregation
app.on_updated += materialize_latestentities_via_aggregation
app.on_deleted_item += materialize_latestentities_via_aggregation
app.on_deleted += materialize_latestentities_via_aggregation

app.on_post_GET_systemvthingsendpoint += push_systemvthings_locally



# we can use the following to customize connection to cluster system database
app.config.update({"SYSMONGO_PORT": 30219})



mongo = app.data.driver
with app.app_context():

    mongo.db.drop_collection("entities")
    mongo.db.create_collection("entities", capped=True, size=5242880)
    mongo.db.entities.create_index([("location.value", "2dsphere")])
    mongo.db.drop_collection("latestentities")
    mongo.db.create_collection("latestentities")
    mongo.db.latestentities.create_index([("location.value", "2dsphere")])


    # the available types view is constructed on top of the latestentities view,
    # so that if a novel entity has replaced an old instance of the same Entity
    # and the new one does not have a pecific Attribute, it will not show up in the types.
    # Also, if the new Entity was produced by a different vThing, then the old vThing
    # will not show uo inside the type.
    mongo.db.drop_collection("types_view")
    mongo.db.create_collection(
        'types_view',
        viewOn='latestentities',
        pipeline=[
            # oldest first, normal direction sorting, so that the typeenity's _created will be the _created
            # of the oldest entity, and typeentity's _updated will be the _updated of the newest entity
            {"$sort" : {"_created":1}},
            {"$group" : {
                "_id":"$type",
                #"tempid":{"$last":"$_id"}, # _id will be the _id of the newest entity
                "tempid":{"$last":"$type"}, # this if we want _id=Vehicle
                "_updated":{"$last":"$_updated"},
                "_created":{"$first":"$_created"},
                #"_etag":{"$last":"$_etag"}, # EVE takes care of this
                # the vthingid Property of the Entity that represents an EntityType will be a multi-attribute one,
                # because the same type can be produced by several different vThings.
                # the $addToSet already gives back an array.
                #"vthingid":{"$addToSet":{"type":"Property","value":"$vthingid.value","datasetId":"$vthingid.value"}},
                ### FOR NOW decided to use one single Property with array of values instead
                "tempvthingid":{"$addToSet":"$vthingid.value"},
                "count":{"$sum" : 1},
            }},
            # copy the _id aggregation pivot, which is the measurement type, into a new NGSI-LD "id" field
            {"$set": { "id":"$_id" } },
            # the NGSI-LD type of this kind of typeentities is a meta-type representing the notion of NGSI-LD Entities' type
            {"$set": { "type":"EntityType" } },
            # rename the tempid to _id
            {"$set": { "_id":"$tempid" } },
            {"$unset" : [ "tempid" ] },
            # reshape the count aggregator into a proper NGSI-LD Property
            {"$set": {"count":{"type":"Property","value":"$count"}}},
            # and the others too
            {"$set": {"generatedByVThings":{"type":"Property","value":"$tempvthingid"}}},
            {"$unset" : [ "tempvthingid" ] },
            #{"$unset" : [ "_created", "_updated", "_etag", "_id", "@context" ] }
        ]
    )



    mongo.db.drop_collection("attributes_view")
    mongo.db.create_collection(
        'attributes_view',
        viewOn='latestentities',
        pipeline=[
            #{"$unset" : [ "id", "_created", "_updated", "_etag", "_id", "@context" ] },
            {
                '$project': {
                    # preserve some fields at the upper level, which will end up replicated
                    # into each little unwinded document
                    '_created': 1,
                    '_updated': 1,
                    'type': 1,
                    'vthingid': 1,
                    'x': {
                        '$objectToArray': '$$CURRENT'
                    }
                }
            },
            # create each little unwinded
            # document x, representing the attribute as a self-standing sub-object.
            # The unwind operation generates _id ObectIds for them??
            {'$unwind': '$x'},
            # now remove all little unwinded documents that do not represent
            # attributes we want to groupby
            {
                '$match': {
                    '$and':[
                        {'x.k': {'$ne': '_id'}},
                        {'x.k': {'$ne': '_created'}},
                        {'x.k': {'$ne': '_updated'}},
                        {'x.k': {'$ne': '_etag'}},
                        {'x.k': {'$ne': 'id'}},
                        {'x.k': {'$ne': '@context'}},
                        {'x.k': {'$ne': 'type'}},
                        {'x.k': {'$ne': 'vthingid'}}
                    ]
                }
            },
            # sort them so the _created of each attribute from the $last will make sense
            {"$sort" : {"_created":1}},
            {"$group" : {
                # groupby the attribute name, which is the .k key of each little unwinded
                # document x, representing the attribute as a self-standing sub-object
                "_id":"$x.k",
                #"tempid":{"$last":"$_id"}, # this if we want _id=ObjectID(BLABLA), but it creates duplicates
                "tempid":{"$last":"$x.k"}, # this if we want _id=brandName
                "_updated":{"$last":"$_updated"},
                "_created":{"$first":"$_created"},
                "tempReferencedByType":{"$addToSet":"$type"},
                "tempReferencedByVthing":{"$addToSet":"$vthingid.value"},
                "count":{"$sum" : 1},
            }},
            # copy the _id aggregation pivot, which is the attribute name, into a new NGSI-LD "id" field
            {"$set": { "id":"$_id" } },
            # the NGSI-LD type of this kind of attributeentities is a meta-type representing the notion of NGSI-LD Entities' attribute
            {"$set": { "type":"EntityAttribute" } },
            # rename the tempid to _id
            {"$set": { "_id":"$tempid" } },
            {"$unset" : [ "tempid" ] },
            # reshape the count aggregator into a proper NGSI-LD Property
            {"$set": {"count":{"type":"Property","value":"$count"}}},
            # and the others too
            {"$set": {"usedByEntityTypes":{"type":"Property","value":"$tempReferencedByType"}}},
            {"$set": {"generatedByVThings":{"type":"Property","value":"$tempReferencedByVthing"}}},
            {"$unset" : [ "tempReferencedByType", "tempReferencedByVthing" ] },
        ]
    )



    mongo.db.drop_collection("temporalentities_view")
    mongo.db.create_collection(
        'temporalentities_view',
        viewOn='entities',
        # we group by NGSI-LD "id", it has to be assigned to the _id pivot of the group.
        pipeline=[
            # group them based on the same NGSI-LD id, and keep id and type from the last.
            {"$group" : {
                "_id":"$id",
                "id":{"$last":"$id"},
                "type":{"$last":"$type"},
                "temporalarray":{
                    #push all fields (using $$ROOT), but exclude some
                    "$push": {
                        # (last stage of the push expression stages here we convert back the array to a document (i.e. to an object))
                        "$arrayToObject": {
                            # Rational is to apply a filter to the array obtained by converting the document to array of {"k","v"} pairs
                            "$filter": {
                                "input": { "$objectToArray": "$$ROOT" },
                                "as": "field",
                                # here we match the condition that a field's key must be NE (not equal) to all
                                # all of unwanted fields, in order for the inclusion condition of the filter
                                # to be true
                                "cond": { "$and": [
                                    { "$ne": [ "$$field.k", "id" ] },
                                    { "$ne": [ "$$field.k", "_etag" ] },
                                    { "$ne": [ "$$field.k", "@context" ] },
                                    { "$ne": [ "$$field.k", "_updated" ] },
                                    { "$ne": [ "$$field.k", "type" ] }
                                ] }
                            }
                        }
                    }
                }
            }
            },
        ]
    )


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9090)
