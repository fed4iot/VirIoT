# disable the _links self-referencing additional fields
HATEOAS = False

# my custom regex for names and jobs identifiers:
# can be composed of chars/digits
# max len = 16
names_regex = 'regex("[a-z0-9A-Z]{1,16}")'
# disable default behaviour
RETURN_MEDIA_AS_BASE64_STRING = False

# return media as URL instead
RETURN_MEDIA_AS_URL = True

faces_schema = {
    'job': {'type': 'string', 'required': True},
    'name': {'type': 'string', 'required': True},
    'pic': {'type': 'media', 'required': True}
}

targetfaces = {
    'resource_methods': ['GET','POST'],
    'schema': faces_schema,
    # we use the sub-resources feature of EVE here, so that "job" and "name"
    # fields are captured from the url structure itself
    'url': 'targetfaces/<' + names_regex + ':job>/<' + names_regex + ':name>'
}

recognizedfaces = {
    'resource_methods': ['GET','POST'],
    'schema': faces_schema,
    # we use the sub-resources feature of EVE here, so that "job" and "name"
    # fields are captured from the url structure itself
    'url': 'recognizedfaces/<' + names_regex + ':job>/<' + names_regex + ':name>'
}

DOMAIN = {
    'targetfacesAPI': targetfaces,
    'recognizedfacesAPI': recognizedfaces,
}
