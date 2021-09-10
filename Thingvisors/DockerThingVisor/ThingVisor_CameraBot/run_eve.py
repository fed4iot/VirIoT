import time
import os

from eve import Eve
from flask import request

from eve.io.base import BaseJSONEncoder
from eve.io.mongo import Validator
from eve.methods.post import post_internal
from eve.methods.delete import deleteitem_internal

import constants

#@app.before_request
#def before():
#    print("the request object ready to be processed:", request)
#
#
#@app.after_request
#def after(response):
#    """
#    Your function must take one parameter, a `response_class` object and return
#    a new response object or the same (see Flask documentation).
#    """
#    print("and here we have the response object instead:", response)
#    return response


class UUIDValidator(Validator):
    """
    Extends the base mongo validator adding support for the uuid data-type
    """
    def _validate_type_uuid(self, value):
        if isinstance(value,int):
            if value>=0 and value<constants.NUM_OF_CAMERAS:
                return True

app = Eve(validator=UUIDValidator)


@app.route('/init')
def init():
    deleteitem_internal('cameras', {})
    for i in range(constants.NUM_OF_CAMERAS):
        post_internal('cameras', {"_id": i})
    return "OK"

if __name__ == '__main__':
    # runs eve
    app.run()
