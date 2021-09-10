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
        if(str(uri).upper().startswith("/v2".upper()) == False ):
            uri = "/v2"+uri

        return uri
    except:
        return uri    

def validateMethodPath(method,path):
    try:
        #DEPRECATED
        #if( method.upper() == "POST".upper() and path.upper()=="/v2/op/update".upper()):
        #    return False
        #else:
        #    return True

        return True

    except:
        return False



def processBody(method,uri,body,sPAE,rPAE,noEncryptedKeys):

    bodyBackUp = body

    try:

        #Determine if method / uri is actually comtemplated by the process and run the corresponding process
        #depending de body.
        state = False

        #POST - https://{HOST}:{PORT}/v2/entities
        if (method.upper()=="POST".upper() and uri.upper()=="/v2/entities".upper()):
            body,state = processCypher(body,sPAE,rPAE,noEncryptedKeys)
        else:
            #POST - https://{HOST}:{PORT}/v2/entities/{entityID}/attrs
            if (method.upper()=="POST".upper() and 
                str(uri).upper().startswith("/v2/entities".upper()) and
                str(uri).upper().endswith("/attrs".upper())):

                body,state = processCypher(body,sPAE,rPAE,noEncryptedKeys)

            else:

                #PATCH - https://{HOST}:{PORT}/v2/entities/{entityID}/attrs
                if (method.upper()=="PATCH".upper() and 
                    str(uri).upper().startswith("/v2/entities".upper()) and
                    str(uri).upper().endswith("/attrs".upper())):

                    body,state = processCypher(body,sPAE,rPAE,noEncryptedKeys)

        return body, state
    except:
        return bodyBackUp, False    


#This process consider ONLY a JSON format.
def processCypher(body,sPAE,rPAE,noEncryptedKeys):

    #Here is an example of JSON structure:
    '''
    {
        "id": "Room2",
        "type": "Room",
        "temperature": {
            "value": 23,
            "type": "Float",
            "metadata": {
                "encrypt_cpabe":{
                    "type":"policy",
                    "value":"att1 att2 2of2"
                }
            }
        },
        "pressure": {
            "value": 720,
            "type": "Integer",
            "metadata": {
                "encrypt_cpabe2":{
                    "type":"Text",
                    "value":"admin"
                }
            }
        },
        "color": {
            "value": "Red",
            "type": "Text",
            "metadata": {
                "encrypt_cpabe":{
                    "type":"Text",
                    "value":"att4 att5 2of2"
                }
            }
        }
    }
    '''

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


#This process consider ONLY a JSON format.
def obtainAttributesToCipher(body,sPAE,rPAE,noEncryptedKeys):

    encryptAttributes = []

    try:

        #FIND attributes must be encrypted and append into the array list encryptAttributes.
        for key in body:

            validateCriteria = True

            if(key.lower() not in noEncryptedKeys):

                for i in range(len(rPAE)):

                    if(len(rPAE[i])>0):

                        validateCriteria = True

                        for j in range(len(rPAE[i])):

                            #Obtain criteria.
                            #Uses separator to create a path array into the attribute.

                            pos0=rPAE[i][j][0].split(sPAE)
                            #Uses separator to create a path array into the attribute.
                            pos1=rPAE[i][j][1]

                            bodyAux=body[key]
                            k=0
                            lenPos0 = len(pos0)

                            while(k<lenPos0):

                                findKeyLevel = False

                                for key2 in bodyAux:

                                    if (pos0[k]!="" and pos0[k]==key2) :

                                        #Critera key - OK
                                        findKeyLevel = True

                                        if(k<lenPos0-1): 
                                            newbody = bodyAux[key2]
                                        else:
                                            if(str(pos1)!="") and str(pos1)!=str(bodyAux[key2]):
                                                validateCriteria = False
                                            break
    
                                if(findKeyLevel==False):
                                    validateCriteria = False
                                    break
                                else:
                                    if (k<lenPos0-1):
                                        bodyAux = newbody
                                    k = k + 1
                                                
                            #Critera fails
                            if(validateCriteria == False):
                                break
                            '''    
                            #Critera fails
                            if(validateCriteria == False):
                                break
                            #Critera fails
                            if(validateCriteria == False):
                                break
                            '''    
                        #Critera fails
                        if(validateCriteria == True):
                            break
            else:
                validateCriteria = False

            #print("processCreateEntityBody - resultado ( " + key + ")")
            #print(validateCriteria)

            if(validateCriteria):
                encryptAttributes.append(key)

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
                #Verify, encriptation type.
                if(body[encryptAttributes[m]]["metadata"]["encrypt_cpabe"]["type"]=="policy"): #CPABE ENCRYPTATION

                    #Cipher attribute type
                    codeType, outType = getstatusoutput(["java","-jar","cpabe_cipher.jar",
                    str(body[encryptAttributes[m]]["metadata"]["encrypt_cpabe"]["value"]),
                    str(body[encryptAttributes[m]]["type"])])

                    #Cipher attribute value
                    codeValue, outValue = getstatusoutput(["java","-jar","cpabe_cipher.jar",
                    str(body[encryptAttributes[m]]["metadata"]["encrypt_cpabe"]["value"]),
                    str(body[encryptAttributes[m]]["value"])])

                    if(codeType == 0 and codeValue == 0):
                        #Assign metadata encrypt value from "policy value" to "cipher original type attribute".
                        body[encryptAttributes[m]]["metadata"]["encrypt_cpabe"]["value"] =  outType.decode('utf8').replace("=","")
                        #Assign cipher attribute value
                        body[encryptAttributes[m]]["value"] =  outValue.decode('utf8').replace("=","")
                        #Change attribute type
                        body[encryptAttributes[m]]["type"] = "cyphertext"                  

            except Exception as e:
                print(e)
                return bodyBackUp, False
            
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
    headers['Content-Type'] = 'application/json'
    headers['Fiware-Correlator'] =  uuid.uuid4()

    #Second value is false because API no send Transfer-Encoding=chunked header response.
    return  headers, False


def errorBody(method,code,title,details):

    #return {'error':'BadRequest','description':'service not found'}
    return {"code": code, "error": title, "details": details}

#def errorCode(method):
#
#    return 400