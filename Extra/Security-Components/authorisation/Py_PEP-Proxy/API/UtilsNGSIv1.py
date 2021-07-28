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
        if(str(uri).upper().startswith("/v1".upper()) == False ):
            uri = "/v1"+uri

        return uri
    except:
        return uri

def validateMethodPath(method,path):

    return True

def processBody(method,uri,body,sPAE,rPAE,noEncryptedKeys):

    bodyBackUp = body

    try:

        #Determine if method / uri is actually comtemplated by the process and run the corresponding process
        #depending de body.
        state = False

        #TODO

        body, state = processCypher(body,sPAE,rPAE,noEncryptedKeys)

        return body, state
    except:
        return bodyBackUp, False    

#This process consider ONLY a JSON format.
def processCypher(body,sPAE,rPAE,noEncryptedKeys):

    bodyBackUp = body

    try:

        encryptAttributes,state = obtainAttributesToCipher(body,sPAE,rPAE,noEncryptedKeys)
        if(state == False):
            return bodyBackUp, False

        body,state  = cipherBodyAttributes(body,encryptAttributes)
        if(state == False):
            return bodyBackUp, False

        return body, True

    except:
        return bodyBackUp, False

def obtainAttributesToCipher(body,sPAE,rPAE,noEncryptedKeys):

    encryptAttributes = []

    try:

        #TODO

        return encryptAttributes, True

    except:
        return encryptAttributes, False

def getstatusoutput(command):
    process = Popen(command, stdout=PIPE,stderr=PIPE)
    out, err = process.communicate()

    #print("out")
    #print(out)
    #print("err")
    #print(err)

    return (process.returncode, out)

#This process consider ONLY a JSON format.
def cipherBodyAttributes(body,encryptAttributes):

    bodyBackUp = body

    try:

        #print("body - BEFORE ENCRYPT")
        #print(body)
            
        #Encrypt values of attributes of array list encryptAttributes.
        for m in range(len(encryptAttributes)):
            
            try:
                #TODO
                print(encryptAttributes[m])

            except Exception as e:
                print(e)
                bodyBackUp, False
            
        #print("body - AFTER ENCRYPT")
        #print(body)

        return body, True

    except:
        return bodyBackUp, False


def errorHeaders(method=None,message=None):

    headers = dict()

    '''
    #GET - headersError
    if(method.upper()=="GET"):
    else:
        #POST - headersError
        if(method.upper()=="POST"):
        else: #PATCH - headersError
            if(method.upper()=="PATCH"):
            else:#PUT - headersError                    
                if(method.upper()=="PUT"): 
    '''
    
    #headers['Connection'] = 'Keep-Alive'
    #headers['Content-Length'] =  len(message)
    headers['Access-Control-Allow-Origin'] = '*'
    headers['Content-Type'] = 'application/json'
    headers['Fiware-Correlator'] =  uuid.uuid4()

    #Second value is false because API no send Transfer-Encoding=chunked header response.
    return  headers, False

def errorBody(method,code,title,details):

    #return {"orionError":{"code":"400","reasonPhrase":"Bad Request","details":"service not found"}}
    return {"code": code, "error": title, "details": details}

#def errorCode(method):
#
#    return 400    