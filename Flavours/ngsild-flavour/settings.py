DEBUG = True

ITEM_URL = 'regex("[\x00-\x7F]+")'
ITEM_LOOKUP = False

URL_PREFIX = 'ngsi-ld'
API_VERSION = 'v1'

CACHE_CONTROL = 'max-age=10,must-revalidate',
############# BUG
#CACHE_EXPIRES = '10', 

schema_for_entities = {
    # Schema definition, based on Cerberus grammar. Check the Cerberus project
    # (https://github.com/pyeve/cerberus) for details.
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

entities_endpoint = {
    # We choose to override global cache-control directives for this resource.
    'cache_control': 'max-age=10,must-revalidate',
    'cache_expires': 10,
    'resource_methods': ['GET', 'POST'],
    # 'title' tag used in item links. Defaults to the resource title minus
    # the final, plural 's' (works fine in most cases but not for 'entities' would be entitie)
    'item_title': 'entity',
    'item_lookup': True,
    'item_lookup_field': 'id',
    'item_methods': ['GET', 'DELETE'],
    'allow_unknown': True,
    'schema': schema_for_entities,
}

#attrs_endpoint = {
#    'resource_methods': ['GET', 'POST'],
#    'url': 'entities/<regex("[\x00-\x7F]+"):id>/attrs',
#    'item_title': 'attribute',
#    'item_lookup': False,
#    'allow_unknown': True,
#}

DOMAIN = {
    'entities': entities_endpoint,
}

