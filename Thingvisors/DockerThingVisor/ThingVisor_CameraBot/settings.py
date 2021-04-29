# -*- coding: utf-8 -*-


# Enable reads (GET), inserts (POST) and DELETE for resources/collections
# (if you omit this line, the API will default to ['GET'] and provide
# read-only access to the endpoint).
RESOURCE_METHODS = ['GET']

# Enable reads (GET), edits (PATCH), replacements (PUT) and deletes of
# individual items  (defaults to read-only item access).
ITEM_METHODS = ['GET', 'PATCH']

# disable the _links self-referencing additional fields
HATEOAS = False

PAGINATION = False

SORTING = False

# disable concurrency control of e-tag
IF_MATCH = False


schema = {
    # Schema definition, based on Cerberus grammar. Check the Cerberus project
    # (https://github.com/pyeve/cerberus) for details.
    '_id': {
        'type': 'uuid', # custom type for the id field
        'unique': True,
        'required': True,
    },
    'data': {
        'type': 'media',
        'required': False,
    },
    'timestamp': {
        'type': 'datetime',
        'required': False,
    },
}

schema2 = {
    # Schema definition, based on Cerberus grammar. Check the Cerberus project
    # (https://github.com/pyeve/cerberus) for details.
    '_id': {
        'type': 'uuid', # custom type for the id field
        'unique': True,
        'required': True,
    },
    'ip': {
        'type': 'string',
        'required': False,
    },
    'port': {
        'type': 'string',
        'required': False,
    },
}

cameras = {
    # 'title' tag used in item links. Defaults to the resource title minus
    # the final, plural 's' (works fine in most cases but not for 'people')
    'item_title': 'camera',
    'item_url': 'int', # specifies that the url for the item must be interpreted as an integer

    # # by default the standard item entry point is defined as
    # # '/people/<ObjectId>'. We leave it untouched, and we also enable an
    # # additional read-only entry point. This way consumers can also perform
    # # GET requests at '/people/<lastname>'.
    # 'additional_lookup': {
    #     'url': 'regex("[0-9]+")',
    #     'field': 'index'
    # },

    # We choose to override global cache-control directives for this resource.
    'cache_control': 'no-cache',
    
    'schema': schema
}

robots = {
    'item_title': 'robot',
    'item_url': 'int',
    'cache_control': 'no-cache',
    'schema': schema2
}

DOMAIN = {"cameras": cameras, "robots": robots}
DEBUG=True


# Let's just use the local mongod instance. Edit as needed.

# Please note that MONGO_HOST and MONGO_PORT could very well be left
# out as they already default to a bare bones local 'mongod' instance.
MONGO_HOST = '127.0.0.1'
MONGO_PORT = 27017
#MONGO_HOST = '192.168.1.3'
#MONGO_PORT = 28000

# # Skip this block if your db has no auth. But it really should.
# MONGO_USERNAME = '<your username>'
# MONGO_PASSWORD = '<your password>'
# # Name of the database on which the user can be authenticated,
# # needed if --auth mode is enabled.
# MONGO_AUTH_SOURCE = '<dbname>'

# MONGO_DBNAME = 'apitest'

