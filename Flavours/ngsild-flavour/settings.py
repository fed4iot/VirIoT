
import copy

DEBUG = True

ITEM_LOOKUP = False

URL_PREFIX = 'ngsi-ld'
API_VERSION = 'v1'

CACHE_CONTROL = 'max-age=10,must-revalidate'

JSON_REQUEST_CONTENT_TYPES = ['application/json', 'application/ld+json']

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

schema_without_unicity_restraint = copy.deepcopy(schema_for_entities)
schema_without_unicity_restraint['id'].pop('unique')

entities_via_attrs_endpoint = {
    # since we are using a regexp in the url, leaving the title = url gives some
    # XML printing issues of the regexp characters of the url. Hence we redefine it.
    'resource_title': 'entity',
    'cache_expires': 10,
    'resource_methods': ['POST'],
    'allow_unknown': True,
    'schema': schema_without_unicity_restraint,
    # ids can be composed of "minus" "column" and chars/digits
    'url': 'entities/<regex("[-a-z0-9:A-Z]{1,100}"):id>/attrs',
    'datasource': {
      'source': 'entities',
    },
    'mongo_indexes': {
      'autoexpiryatsomepoint': ([('_created', 1)], { 'expireAfterSeconds': 120}),
    }
}

entities_endpoint = {
    'cache_expires': 10,
    'resource_methods': ['GET', 'POST'],
    'item_lookup': True,
    'item_methods': ['GET', 'DELETE'],
    'item_lookup_field': 'id',
    'item_url': 'regex("[-a-z0-9:A-Z]{1,100}")',
    'allow_unknown': True,
    'schema': schema_for_entities,
    'url': "entities",
    'datasource': {
      'source': 'entities',
    }
}

DOMAIN = {
    'dummy1': entities_via_attrs_endpoint,
    'dummy2': entities_endpoint,
}
