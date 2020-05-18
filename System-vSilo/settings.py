
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


# to match NGSI-LD spec for query keyword
QUERY_WHERE = 'q'


# my custom regex for URIs:
# ids can be composed of "minus" "colon" "underscore" and chars/digits
# max len = 100
uri_regex = 'regex("[-a-z0-9:A-Z_]{1,100}")'


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

schema_for_entities_without_unicity_restraint = copy.deepcopy(schema_for_entities)
schema_for_entities_without_unicity_restraint['id'].pop('unique')




entities_POST_DELETE_datasource_filter = {
  # specify the mongodb collection that the endpoint will target.
  # We pput it here so both endpoints can target the same collection
  'source': 'entities',
}
entities_POST_attrs_endpoint = {
    # since we are using a regexp in the url, leaving the default resource_title = url gives some
    # XML printing issues of the regexp characters of the url. Hence we redefine it.
    'resource_title': 'entity',
    # in case we want caching
    #'cache_expires': 10,
    # /entities/eid/attrs POST is used for Append Entity Attributes 6.6.3.1 -> 5.6.3 (returns 404 Not Found)
    #                          (&options=noOverwrite can be used. By default, Attributes will be overwritten)
    'resource_methods': ['POST'],
    # in entities this is important for the NGSI-LD Attributes
    'allow_unknown': True,
    'schema': schema_for_entities_without_unicity_restraint,
    # we use the sub-resources feature of EVE here
    'url': 'entities/<' + uri_regex + ':id>/attrs',
    'datasource': entities_POST_DELETE_datasource_filter,
    # dont need the following TTL expiry index anymore, converting entities collection to capped size
    # at eve app initialization
    #'mongo_indexes': {
    #  'autoexpiryatsomepoint': ([('_created', 1)], { 'expireAfterSeconds': 900}),
    #}
}
entities_POST_DELETE_endpoint = {
    'url': "entities",
    'resource_title': 'entity',
    # in case we want caching
    #'cache_expires': 10,
    # /entities POST is used for Create Entity 6.4.3.1 -> 5.6.1 (returns 409 Already Exists)
    'resource_methods': ['POST'],
    'item_lookup': True,
    #/entities/eid DELETE is used for Delete Entity 6.5.3.2 -> 5.6.6 (returns 404 Not Found)
    'item_methods': ['DELETE'],
    'item_lookup_field': 'id',
    'item_url': uri_regex,
    'allow_unknown': True,
    'schema': schema_for_entities,
    'datasource': entities_POST_DELETE_datasource_filter,
}




entities_GET_datasource_filter = {
  # this endpoint targets a mongodb view (created outside of settings, at initialization of EVE app)
  'source': 'latestentities',
}
entities_GET_endpoint = {
  'url': "entities",
  'resource_title': 'entity',
  # /entities GET is used for querying 6.4.3.2 -> 5.7.2 (&q, &attrs, etc...)  
  'resource_methods': ['GET'],
  'item_lookup': True,
  #/entities/eid GET is used for Retrieve Entity 6.5.3.1 -> 5.7.1 (returns 404 Not Found)
  #                  (&attrs can be used to retrieve some Attributes only)
  'item_methods': ['GET'],
  'item_lookup_field': 'id',
  'item_url': uri_regex,
  'allow_unknown': True,
  'schema': schema_for_entities_without_unicity_restraint,
  'datasource': entities_GET_datasource_filter,
}




types_datasource_filter = {
  # this endpoint targets a mongodb view (created outside of settings, at initialization of EVE app)
  'source': 'types_view',
}
types_endpoint = {
  'url': "types",
  'resource_title': 'type',
  'resource_methods': ['GET'],
  'item_lookup': True,
  'item_methods': ['GET'],
  'item_lookup_field': 'id',
  'item_url': uri_regex,
  'allow_unknown': True,
  'schema': schema_for_entities_without_unicity_restraint,
  'datasource': types_datasource_filter,
}




attributes_datasource_filter = {
  # this endpoint targets a mongodb view (created outside of settings, at initialization of EVE app)
  'source': 'attributes_view',
}
attributes_endpoint = {
  'url': "attributes",
  'resource_title': 'attribute',
  'resource_methods': ['GET'],
  'item_lookup': True,
  'item_methods': ['GET'],
  'item_lookup_field': 'id',
  'item_url': uri_regex,
  'allow_unknown': True,
  'schema': schema_for_entities_without_unicity_restraint,
  'datasource': attributes_datasource_filter,
}




temporalentities_datasource_filter = {
  # this endpoint targets a mongodb view (created outside of settings, at initialization of EVE app)
  'source': 'temporalentities_view',
}
temporalentities_endpoint = {
  'url': "temporal/entities",
  'resource_title': 'entity',
  'resource_methods': ['GET'],
  'item_lookup': True,
  'item_methods': ['GET'],
  'item_lookup_field': 'id',
  'item_url': uri_regex,
  'allow_unknown': True,
  'schema': schema_for_entities_without_unicity_restraint,
  'datasource': temporalentities_datasource_filter,
}




SYSMONGO_HOST = '13.80.153.4'
SYSMONGO_PORT = 30219
#SYSMONGO_USERNAME = 'admin'
#SYSMONGO_PASSWORD = 'passw0rd'
SYSMONGO_DBNAME = 'viriotDB'
systemvthings_datasource_filter = {
  # this endpoint targets an external collection, coming from an external mongo server
  # i.e. the fed4iot system database
  'source': 'thingVisorC',
  'aggregation': {
    'pipeline': [
    {
        '$unwind': '$vThings'
    }, {
        '$addFields': {
            'vThings.tvDescription': '$tvDescription'
        }
    }, {
        '$replaceRoot': {
            'newRoot': '$vThings'
        }
    }, {
        '$project': {
            'id': '$id',
            #'id': {"$replaceOne": { "input": "$id", "find": "/", "replacement": ":" }},
            #'_id': '$id', 
            #'_created': '$$NOW', 
            #'_updated': '$$NOW', 
            'type': 'viriotVThing', 
            'kind': {
                'type': 'Property', 
                'value': '$type'
            }, 
            'label': {
                'type': 'Property', 
                'value': '$label'
            }, 
            'description': {
                'type': 'Property', 
                'value': '$description'
            }, 
            'tvDescription': {
                'type': 'Property', 
                'value': '$tvDescription'
            }
        }
      }
    ]
  }
}
systemvthings_endpoint = {
  'url': "systemvthings",
  'resource_title': 'systemvthing',
  'resource_methods': ['GET'],
  'schema': schema_for_entities_without_unicity_restraint,
  'datasource': systemvthings_datasource_filter,
  'mongo_prefix': 'SYSMONGO',
  # lets get all of them from system db
  'pagination': False,
}





DOMAIN = {
  'entitiesPOSTattrsendpoint': entities_POST_attrs_endpoint,
  'entitiesPOSTDELETEendpoint': entities_POST_DELETE_endpoint,
  'entitiesGETendpoint': entities_GET_endpoint,
  'temporalentitiesendpoint': temporalentities_endpoint,
  'typesendpoint': types_endpoint,
  'attributesendpoint': attributes_endpoint,
  'systemvthingsendpoint': systemvthings_endpoint,
}
