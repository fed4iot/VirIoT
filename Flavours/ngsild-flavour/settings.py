
import copy

DEBUG = True

ITEM_LOOKUP = False

URL_PREFIX = 'ngsi-ld'
API_VERSION = 'v1'

# in case we want caching
#CACHE_CONTROL = 'max-age=10,must-revalidate'

JSON_REQUEST_CONTENT_TYPES = ['application/json', 'application/ld+json']

# disable the _links self-referencing additional fields
HATEOAS = False

schema_for_entities = {
    'id': {
        'type': 'string',
        'required': True,
        'unique': True,
    },
    'type': {
        'type': 'string',
        'required': True,
    },
}

entities_datasource_properties = {
  # specify the mongodb collection that the endpoint will target.
  # We pput it here so both endpoints can target the same collection
  'source': 'entities',
  # specify a projection, which is the tool to hide some fields (set to zero (set to one would only include those))
  #'projection': {
  #  'id': 1,
  #  'type': 1,
    #'_id': 0,
    #'_etag': 0,
    #'_updated': 0,
    #'_created': 0,
    #'_links': 0,
  #},
}

schema_without_unicity_restraint = copy.deepcopy(schema_for_entities)
schema_without_unicity_restraint['id'].pop('unique')

entities_via_attrs_endpoint = {
    # since we are using a regexp in the url, leaving the default resource_title = url gives some
    # XML printing issues of the regexp characters of the url. Hence we redefine it.
    'resource_title': 'entity',
    # in case we want caching
    #'cache_expires': 10,
    # /entities/eid/attrs POST is used for Append Entity Attributes 6.6.3.1 -> 5.6.3 (returns 404 Not Found)
    #                          (&options=noOverwrite can be used. By default, Attributes will be overwritten)
    'resource_methods': ['POST'],
    'allow_unknown': True,
    'schema': schema_without_unicity_restraint,
    # ids can be composed of "minus" "column" and chars/digits
    'url': 'entities/<regex("[-a-z0-9:A-Z]{1,100}"):id>/attrs',
    'datasource': entities_datasource_properties,
    'mongo_indexes': {
      'autoexpiryatsomepoint': ([('_created', 1)], { 'expireAfterSeconds': 900}),
    }
}

entities_endpoint = {
    # in case we want caching
    #'cache_expires': 10,
    # /entities GET is used for querying 6.4.3.2 -> 5.7.2 (&q, &attrs, etc...)
    # /entities POST is used for Create Entity 6.4.3.1 -> 5.6.1 (returns 409 Already Exists)
    'resource_methods': ['GET', 'POST'],
    'item_lookup': True,
    #/entities/eid GET is used for Retrieve Entity 6.5.3.1 -> 5.7.1 (returns 404 Not Found)
    #                  (&attrs can be used to retrieve some Attributes only)
    #/entities/eid DELETE is used for Delete Entity 6.5.3.2 -> 5.6.6 (returns 404 Not Found)
    'item_methods': ['GET', 'DELETE'],
    'item_lookup_field': 'id',
    'item_url': 'regex("[-a-z0-9:A-Z]{1,100}")',
    'allow_unknown': True,
    'schema': schema_for_entities,
    'url': "entities",
    'datasource': entities_datasource_properties,
}


types_datasource_properties = {
  # all endpoints can target the same collection
  'source': 'entities',
  # we group by "type", it has to be assigned to the _id of the item.
  # we add a count to occurrences of each type.
  # and its umbrella vthingid. BTW if type is the same, then vthingid is the same.
  'aggregation' : {
    'pipeline': [
      {"$group" : {"_id":"$type", "vthingid":{"$last":"$vthingid"}, "count":{"$sum" : 1}}},
      # rename the _id newly aggregated, which is the type, into "type"
      {"$set" : { "type":"$_id" } },
      {"$unset" : [ "_created", "_updated", "_etag", "_id", "@context" ] }
    ]
  }
}

types_endpoint = {
  'url': "types",
  'resource_title': 'type',
  'resource_methods': ['GET'],
  'datasource': types_datasource_properties,
}


latestentities_datasource_properties = {
  # all endpoints can target the same collection
  'source': 'entities',
  # we group by NGSI-LD "id", it has to be assigned to the _id of the item.
  # we add a count to occurrences of each type.
  # and its umbrella vthingid. BTW if NGSI-LD id is the same, then vthingid is the same.
  # $$ROOT to keep the whole document per each name followed by $replaceRoot to promote the document to the top.
  # https://stackoverflow.com/questions/52566913/how-to-group-in-mongodb-and-return-all-fields-in-result
  'aggregation' : {
    'pipeline': [
      # oldest first, normal direction sorting
      {"$sort" : {"_created":1}},
      {"$group" : {"_id":"$id", "vthingid":{"$last":"$vthingid"},"doc":{"$last":"$$ROOT"}}}, #pick fields from last
      {"$replaceRoot":{"newRoot":"$doc"}},
      {"$unset" : [ "_created", "_updated", "_etag", "_id", "@context" ] }
    ]
  }
}

latestentities_endpoint = {
  'url': "latestentities",
  'resource_title': 'lastentity',
  'resource_methods': ['GET'],
  'datasource': latestentities_datasource_properties,
}


DOMAIN = {
    'dummy1': entities_via_attrs_endpoint,
    'dummy2': entities_endpoint,
    'dummy3': types_endpoint,
    'dummy4': latestentities_endpoint,
}
