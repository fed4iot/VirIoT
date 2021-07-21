#
#Copyright Odin Solutions S.L. All Rights Reserved.
#
#SPDX-License-Identifier: Apache-2.0
#

import json
import uuid
#import os
from subprocess import Popen, PIPE

def processUri(uri):
    try:
        
        return uri
    except:
        return uri    

def validateMethodPath(method,path):
    try:

        return True

    except:
        return False


def errorHeaders(method=None,message=None):

    headers = dict()

    headers['Content-Type'] = 'application/json'

    #Second value is false because API no send Transfer-Encoding=chunked header response.
    return  headers, False


def errorBody(method,code,title,details):

    #return {'error':'BadRequest','description':'service not found'}
    return {"code": code, "error": title, "details": details}

#def errorCode(method):
#
#    return 400