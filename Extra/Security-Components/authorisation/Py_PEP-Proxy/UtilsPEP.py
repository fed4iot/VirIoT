#
#Copyright Odin Solutions S.L. All Rights Reserved.
#
#SPDX-License-Identifier: Apache-2.0
#

import json
import API.UtilsNGSIv1,API.UtilsNGSIv2,API.UtilsNGSILDv1,API.UtilsGenericAPI,API.UtilsFed4IoTMC
import sys
sys.path.insert(0, './API')

def obtainValidUri(APIVersion,uri):

    try:

        if( APIVersion.upper() == "NGSIv1".upper()):
            uri = API.UtilsNGSIv1.processUri(uri)
        else:
            if( APIVersion.upper() == "NGSIv2".upper()):
                uri = API.UtilsNGSIv2.processUri(uri)
            else:     
                if ( APIVersion.upper() == "NGSILDv1".upper()):
                    uri = API.UtilsNGSILDv1.processUri(uri)
                else:
                    if ( APIVersion.upper() == "GenericAPI".upper()):
                        uri = API.UtilsGenericAPI.processUri(uri)
                    else:
                        if ( APIVersion.upper() == "Fed4IoTMC".upper()):
                            uri = API.UtilsFed4IoTMC.processUri(uri)
        return  uri

    except:
        return uri

#Validate Not supported method/path pairs.
def validateNotSupportedMethodPath(APIVersion,method,path):

    try:
        testSupported = False

        if( APIVersion.upper() == "NGSIv1".upper()):
            testSupported = API.UtilsNGSIv1.validateMethodPath(method,path)
        else:
            if( APIVersion.upper() == "NGSIv2".upper()):
                testSupported = API.UtilsNGSIv2.validateMethodPath(method,path)
            else:     
                if ( APIVersion.upper() == "NGSILDv1".upper()):
                    testSupported = API.UtilsNGSILDv1.validateMethodPath(method,path)
                else:
                    if ( APIVersion.upper() == "GenericAPI".upper()):
                        testSupported = API.UtilsGenericAPI.validateMethodPath(method,path)
                    else:
                        if ( APIVersion.upper() == "Fed4IoTMC".upper()):
                            testSupported = API.UtilsFed4IoTMC.validateMethodPath(method,path)

        return testSupported

    except:
        return False


def encryptProcess(APIVersion,method,uri,body,sPAE,rPAE,noEncryptedKeys):

    bodyBackUp = body

    try:

        state = True
        #To enter en encryptation is necessary any encriptation criteria is defined.
        if (len(rPAE) > 0 or len(rPAE)):

            #Actualy only contemplate "POST" and "PATCH" methods from NGSIv1, NGSIv2, NGSILDv1
            if ((APIVersion.upper() == "NGSIv1".upper() or  
                APIVersion.upper() == "NGSIv2".upper() or 
                APIVersion.upper() == "NGSILDv1".upper()) and         
                body != None and method.upper() in ["POST".upper(),"PATCH".upper()]):

                state = False

                #Convert from byte to JSON (dict)
                bodyInProcess = json.loads(body.decode('utf8').replace("'", '"'))

                #CASE API version using differents proccess encryptation.
                if( APIVersion.upper() == "NGSIv1".upper()):
                    bodyInProcess,state = API.UtilsNGSIv1.processBody(method,uri,bodyInProcess,sPAE,rPAE,noEncryptedKeys)
                else:
                    if( APIVersion.upper() == "NGSIv2".upper()):
                        bodyInProcess,state = API.UtilsNGSIv2.processBody(method,uri,bodyInProcess,sPAE,rPAE,noEncryptedKeys)
                    else:     
                        if ( APIVersion.upper() == "NGSILDv1".upper()):
                            bodyInProcess,state = API.UtilsNGSILDv1.processBody(method,uri,bodyInProcess,sPAE,rPAE,noEncryptedKeys)

                bodyInProcessStr=json.dumps(bodyInProcess)
                body = bodyInProcessStr.encode()

                #print("body calculado")
                #print(body)
                #print(type(body))

        #return bodyInProcess
        return body,state

    except:
        return bodyBackUp, False

def obtainErrorResponseHeaders(APIVersion,method=None,message=None):

    headers = dict()
    chunkedResponse = False

    if( APIVersion.upper() == "NGSIv1".upper()):
        headers,chunkedResponse = API.UtilsNGSIv1.errorHeaders()
    else:
        if( APIVersion.upper() == "NGSIv2".upper()):
            headers,chunkedResponse = API.UtilsNGSIv2.errorHeaders()
        else:     
            if ( APIVersion.upper() == "NGSILDv1".upper()):
                headers,chunkedResponse = API.UtilsNGSILDv1.errorHeaders()
            else:
                if ( APIVersion.upper() == "GenericAPI".upper()):
                    headers,chunkedResponse = API.UtilsGenericAPI.errorHeaders()
                else:
                    if ( APIVersion.upper() == "Fed4IoTMC".upper()):
                        headers,chunkedResponse = API.UtilsFed4IoTMC.errorHeaders()

    return  headers,chunkedResponse


def obtainErrorResponseBody(APIVersion,method,code,title,details):

    if( APIVersion.upper() == "NGSIv1".upper()):
        messageBody = API.UtilsNGSIv1.errorBody(method,code,title,details)
    else:
        if( APIVersion.upper() == "NGSIv2".upper()):
            messageBody = API.UtilsNGSIv2.errorBody(method,code,title,details)
        else:     
            if ( APIVersion.upper() == "NGSILDv1".upper()):
                messageBody = API.UtilsNGSILDv1.errorBody(method,code,title,details)
            else:
                if ( APIVersion.upper() == "GenericAPI".upper()):
                    messageBody = API.UtilsGenericAPI.errorBody(method,code,title,details)
                else:
                    if ( APIVersion.upper() == "Fed4IoTMC".upper()):
                        messageBody = API.UtilsFed4IoTMC.errorBody(method,code,title,details)

    return messageBody


#def obtainErrorResponseCode(APIVersion,method):
#
#    if( APIVersion.upper() == "NGSIv1".upper()):
#        code = API.UtilsNGSIv1.errorCode(method)
#    else:
#        if( APIVersion.upper() == "NGSIv2".upper()):
#            code = API.UtilsNGSIv2.errorCode(method)
#        else:     
#            if ( APIVersion.upper() == "NGSILDv1".upper()):
#                code = API.UtilsNGSILDv1.errorCode(method)
#    
#    return code
