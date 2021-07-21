#
#Copyright Odin Solutions S.L. All Rights Reserved.
#
#SPDX-License-Identifier: Apache-2.0
#

from http.server import HTTPServer, BaseHTTPRequestHandler
import ssl
import http.client
import logging
import sys
import json
import configparser
import UtilsPEP
from subprocess import Popen, PIPE
import html
import os
from socketserver import ThreadingMixIn
import threading

import time

#import numpy as np


#  "ProxyPrivKey": "certs/server-priv-rsa.pem",
#  "ProxyPubKey": "certs/server-pub-rsa.pem",
#  "ProxyCert": "certs/server-public-cert.crt",

#Obtain configuracion from config.cfg file.
cfg = configparser.ConfigParser()  
cfg.read(["./config.cfg"])  
pep_host = cfg.get("GENERAL", "pep_host")
pep_port = int(cfg.get("GENERAL", "pep_port"))

#APIVersion = cfg.get("GENERAL", "APIVersion")

#target_protocol = cfg.get("GENERAL", "target_protocol")
#target_host = cfg.get("GENERAL", "target_host")
#target_port = int(cfg.get("GENERAL", "target_port"))

#blockchain_usevalidation=int(cfg.get("GENERAL", "blockchain_usevalidation"))
#blockchain_protocol = cfg.get("GENERAL", "blockchain_protocol")
#blockchain_host = cfg.get("GENERAL", "blockchain_host")
#blockchain_port = int(cfg.get("GENERAL", "blockchain_port"))

target_protocol = str(os.getenv('target_protocol'))
target_host = str(os.getenv('target_host'))
target_port = int(os.getenv('target_port'))
APIVersion = str(os.getenv('target_API'))

blockchain_usevalidation = int(os.getenv('blockchain_usevalidation'))
blockchain_protocol = str(os.getenv('blockchain_protocol'))
blockchain_host = str(os.getenv('blockchain_host'))
blockchain_port = int(os.getenv('blockchain_port'))

fed4iotmc_protocol = str(os.getenv('fed4iotmc_protocol'))
fed4iotmc_host = str(os.getenv('fed4iotmc_host'))
fed4iotmc_port = int(os.getenv('fed4iotmc_port'))
fed4iotmc_authz_testpath = str(os.getenv('fed4iotmc_authz_testpath'))
fed4iotmc_login_path = str(os.getenv('fed4iotmc_login_path'))
fed4iotmc_login_userID = str(os.getenv('fed4iotmc_login_userID'))
fed4iotmc_login_password = str(os.getenv('fed4iotmc_login_password'))

fed4iotmc_JWT = ""

try:
    pep_protocol = str(os.getenv('pep_protocol'))
except Exception as e:
    logging.info(e)
    pep_protocol = "https"

if (str(pep_protocol).upper() == "None".upper()) :
    pep_protocol = "https"

chunk_size=int(cfg.get("GENERAL", "chunk_size"))

allApiHeaders=json.loads(cfg.get("GENERAL", "allApiHeaders"))

#Obtain API headers
for m in range(len(allApiHeaders)):
    if(allApiHeaders[m][0].upper()==APIVersion.upper()):
        apiHeaders = allApiHeaders[m][1]
        break

allSeparatorPathAttributeEncriptation=json.loads(cfg.get("GENERAL", "allSeparatorPathAttributeEncriptation"))

#Obtain API separator
for m in range(len(allSeparatorPathAttributeEncriptation)):
    if(allSeparatorPathAttributeEncriptation[m][0].upper()==APIVersion.upper()):
        sPAE = allSeparatorPathAttributeEncriptation[m][1]
        break

rPAE=json.loads(cfg.get("GENERAL", "relativePathAttributeEncriptation"))
noEncryptedKeys = json.loads(cfg.get("GENERAL", "noEncryptedKeys"))

tabLoggingString = "\t\t\t\t\t\t\t"

pep_device = str(os.getenv('PEP_ENDPOINT'))

logginKPI = cfg.get("GENERAL", "logginKPI")

def CBConnection(method, uri,headers,body = None):

    global fed4iotmc_JWT

    try:

        #logging.info("")
        #logging.info("")
        #logging.info("********* CBConnection *********")

        uri = UtilsPEP.obtainValidUri(APIVersion,uri)

        #logging.info("CBConnection: Sending the Rquest")

        # send some data
   
        if(target_protocol.upper() == "http".upper() or target_protocol.upper() == "https".upper()):

            state = True

            if (body != None and str(uri).upper().startswith("/v1/subscribeContext".upper()) == False 
                and str(uri).upper().startswith("/v2/subscriptions".upper()) == False 
                and str(uri).upper().startswith("/ngsi-ld/v1/subscriptions".upper()) == False
                and str(uri).upper().startswith("/v2/op/update".upper()) == False):
            
                state = False

                #logging.info("Original body request: ")
                #logging.info(str(body))
               
                milli_secEP=0
                milli_secEP2=0

                milli_secEP=int(round(time.time() * 1000))

                body, state = UtilsPEP.encryptProcess(APIVersion,method,uri,body,sPAE,rPAE,noEncryptedKeys)
                #body = html.escape(body)
                
                #logging.info("Body request AFTER encryption process: ")
                #logging.info(str(body))

                milli_secEP2=int(round(time.time() * 1000))

                if(logginKPI.upper()=="Y".upper()):
                    logging.info("")
                    logging.info("")
                    logging.info("Total(ms) Encrypt process: " + str(milli_secEP2 - milli_secEP))

            if (state):

                if(target_protocol.upper() == "http".upper()):
                    conn = http.client.HTTPConnection(target_host, target_port)
                else:                    
                    gcontext = ssl.SSLContext()
                    conn = http.client.HTTPSConnection(target_host,target_port,
                                                context=gcontext)


                #Deleting "x-auth-token" header, before NGSILD, REQUEST.

                if headers.get("x-auth-token"): 
                    headers.pop("x-auth-token")

                if ( APIVersion.upper() == "Fed4IoTMC".upper()):
                    headers["Authorization"] = "Bearer " + fed4iotmc_JWT

                logging.info("")
                logging.info("")
                logging.info("API REQUEST:\n" + 
                tabLoggingString + "- Host: " + target_host + "\n" + 
                tabLoggingString + "- Port: " + str(target_port) + "\n" + 
                tabLoggingString + "- Method: " + method + "\n" + 
                tabLoggingString + "- URI: " + uri + "\n" + 
                tabLoggingString + "- Headers: " + str(headers) + "\n" + 
                tabLoggingString + "- Body: " + str(body))

                conn.request(method, uri, body, headers)
                response = conn.getresponse()

                #logging.info("CBConnection - RESPONSE")
                logging.info("API RESPONSE CODE: "      + str(response.code))
                #logging.info("Headers: ")
                #logging.info(response.headers)
            else:
                return -1
        
        #logging.info("********* CBConnection - END ********* ")

        return response

    except Exception as e:
        logging.info(e)
        return -1

def BlockChainConnection(method, uri, headers = {}, body = None):

    try:

        #logging.info("")
        #logging.info("")
        #logging.info("********* BlockChainConnection *********")

        # send some data
        
        if(blockchain_protocol.upper() == "http".upper() or blockchain_protocol.upper() == "https".upper()):

            if(blockchain_protocol.upper() == "http".upper()):
                conn = http.client.HTTPConnection(blockchain_host, blockchain_port)
            else:                    
                
                gcontext = ssl.SSLContext()
                conn = http.client.HTTPSConnection(blockchain_host,blockchain_port,
                                                context=gcontext)

            logging.info("BLOCKCHAIN REQUEST:\n" +
                         tabLoggingString + "- Host: " + blockchain_host + "\n" + 
                         tabLoggingString + "- Port: " + str(blockchain_port) + "\n" + 
                         tabLoggingString + "- Method: " + method + "\n" + 
                         tabLoggingString + "- URI: " + uri + "\n" + 
                         tabLoggingString + "- Headers: " + str(headers) + "\n" + 
                         tabLoggingString + "- Body: " + str(body))

            conn.request(method, uri, body, headers)

            response = conn.getresponse()

            #logging.info("BlockChainConnection - RESPONSE")
            logging.info(" SUCCESS : BlockChain response - code: "      + str(response.code))
            #logging.info("Headers: ")
            #logging.info(response.headers)
        
        #logging.info("********* BlockChainConnection - END *********")

        return response

    except Exception as e:
        logging.info(e)
        return -1


def MasterControllerConnection(method, uri, headers = {}, body = None):

    try:

        #logging.info("")
        #logging.info("")
        #logging.info("********* MasterControllerConnection *********")

        # send some data
        
        if(fed4iotmc_protocol.upper() == "http".upper() or fed4iotmc_protocol.upper() == "https".upper()):

            if(fed4iotmc_protocol.upper() == "http".upper()):
                conn = http.client.HTTPConnection(fed4iotmc_host, fed4iotmc_port)
            else:                    
                
                gcontext = ssl.SSLContext()
                conn = http.client.HTTPSConnection(fed4iotmc_host,fed4iotmc_port,
                                                context=gcontext)

            logging.info("MASTER-CONTROLLER REQUEST:\n" +
                         tabLoggingString + "- Host: " + fed4iotmc_host + "\n" + 
                         tabLoggingString + "- Port: " + str(fed4iotmc_port) + "\n" + 
                         tabLoggingString + "- Method: " + method + "\n" + 
                         tabLoggingString + "- URI: " + uri + "\n" + 
                         tabLoggingString + "- Headers: " + str(headers) + "\n" + 
                         tabLoggingString + "- Body: " + str(body))

            conn.request(method, uri, body, headers)

            response = conn.getresponse()

            #logging.info("MasterControllerConnection - RESPONSE")
            logging.info(" SUCCESS : Master-Controller response - code: "      + str(response.code))
            #logging.info("Headers: ")
            #logging.info(response.headers)
        
        #logging.info("********* MasterControllerConnection - END *********")

        return response

    except Exception as e:
        logging.info(e)
        return -1


def getstatusoutput(command):
    process = Popen(command, stdout=PIPE,stderr=PIPE)
    out, err = process.communicate()

    return (process.returncode, out)

def obtainRequestHeaders(RequestHeaders):

    headers = dict()

    content_length = 0

    try:
        # We get the headers
        
        #logging.info ("********* HEADERS BEFORE obtainRequestHeaders *********")
        #logging.info (RequestHeaders)
        
        for key in RequestHeaders:
            #logging.info("Procesando: " + str(key) + ":" + str(RequestHeaders[key]))

            #value_index=-1
            #
            #try:
            #    #To find only admittable headers from request previously configured in config.cfg file.
            #    value_index = apiHeaders.index(key.lower())
            #
            #    #Supporting all headers
            #    if (value_index == -1 ):
            #        value_index = apiHeaders.index("*")
            #
            #except:
            #    value_index = -1
            #
            ##If the header key was found, it will be considered after.
            #if (value_index > -1 ):
            #
            #    #logging.info("Incluido: " + str(key) + ":" + str(RequestHeaders[key]))
            #
            #    headers[key] = RequestHeaders[key]

            headers[key] = RequestHeaders[key]

            if(key.upper()=="Content-Length".upper()):
                content_length = int(RequestHeaders[key])

    except Exception as e:
        logging.info(e)

        headers["Error"] = str(e)

    #logging.info ("********* HEADERS AFTER obtainRequestHeaders *********")
    #logging.info (headers)

    return headers, content_length

def validationToken(headers,method,uri,body = None):

    validationCapabilityToken = False
    validationBlockChain = False
    validationResult = False

    isRevoked = False
    strRevoked = ""

    outTypeProcessed = ""

    #print("uri: " + uri)

    milli_secValCT=0
    milli_secValCT2=0

    milli_secBC=0
    milli_secBC2=0

    milli_secValCTT=0
    milli_secValCTT2=0

    try:

        milli_secValCTT=int(round(time.time() * 1000))

        for key in headers:

            if(key.upper()=="x-auth-token".upper()):

                headersStr = json.dumps(headers)

                # DEPRECATED NOT USEFULL AND FAILS WITH FORM-DATA BODIES.
                #if (body == None):
                #    bodyStr = "{}"
                #else:
                #    bodyStr = body.decode('utf8').replace("'", '"').replace("\t", "").replace("\n", "")
                #    #bodyStr = body.decode('utf8').replace("'", '"')
                bodyStr = "{}"

                #print(type(str(method)))
                #print(type(str(uri)))
                #print(type(headersStr))
                #print(type(bodyStr))
                #print(type(str(headers[key])))

                #print(str(method))
                #print(str(uri))
                #print(headersStr)
                #print(bodyStr)
                #print(str(headers[key]))

                
                ##Validating token (v1)
                ##Observation: str(uri).replace("&",";") --> for PDP error: "The reference to entity "***" must end with the ';' delimiter.""
                #codeType, outType = getstatusoutput(["java","-jar","CapabilityEvaluator_old.jar",
                ##str(pep_device),
                #str(method),
                #str(uri).replace("&",";"),
                #headersStr, # "{}", #headers
                #bodyStr,
                #str(headers[key])])
                #
                #logging.info("codeType_v0: " + str(codeType))
                #logging.info("outType_v0: " + str(outType))
        
                milli_secValCT=int(round(time.time() * 1000))

                #Validating token (v2)
                #Observation: str(uri).replace("&",";") --> for PDP error: "The reference to entity "***" must end with the ';' delimiter.""
                codeType, outType = getstatusoutput(["java","-jar","CapabilityEvaluator.jar",
                str(pep_device),
                str(method),
                str(uri).replace("&",";"),
                str(headers[key]), #Capability token
                "", #Subject
                headersStr, # "{}", #headers
                bodyStr
                ])

                milli_secValCT2=int(round(time.time() * 1000))

                #logging.info("codeType_v2: " + str(codeType))
                #logging.info("outType_v2: " + str(outType))


                outTypeProcessed = outType.decode('utf8').replace("'", '"').replace("CODE: ","").replace("\n", "")
                #outTypeProcessed = outType.decode('utf8').replace("'", '"').replace("CODE: ","")

                #print("outTypeProcessed: " + outTypeProcessed)

                if (outTypeProcessed.upper()=="AUTHORIZED".upper()):

                    validationCapabilityToken = True

                    if (blockchain_usevalidation == 1):

                        milli_secBC=int(round(time.time() * 1000))

                        capabilityTokenId = json.loads(headers[key])["id"]

                        #Send requests to blockchain to obtain if Capability Token id exists and its 
                        resultGet = BlockChainConnection("GET", "/token/" + capabilityTokenId, {}, None)
                        #resultGet = BlockChainConnection("GET", "/token/43oi76utr62o8fuad5v79duhia", {}, None)


                        errorBlockChainConnectionGET = False
                        try:
                            if(resultGet==-1):
                                errorBlockChainConnectionGET = True
                        except:
                            errorBlockChainConnectionGET = False

                        if (errorBlockChainConnectionGET==False):

                            strDataGET = resultGet.read(chunk_size).decode('utf8')

                            if (resultGet.code!=200):
                                
                                #This request is sent by Capability Manager component.
                                ##If Capability Token id don't exist, send requests to register it.
                                #resultPost = BlockChainConnection("POST", "/token/register", {}, "{\"id\":\"" + capabilityTokenId + "\"}")
                                #
                                #errorBlockChainConnectionPOST = False
                                #try:
                                #    if(resultPost==-1):
                                #        errorBlockChainConnectionPOST = True
                                #except:
                                #    errorBlockChainConnectionPOST = False
                                #
                                #if (errorBlockChainConnectionPOST==False):
                                #
                                #    strDataPOST = resultPost.read(chunk_size).decode('utf8')
                                #
                                #    if (resultPost.code==201):
                                #        validationBlockChain = True
                                #    else:
                                #        headers["Error"] = str("Can't confirm validity state of the registered token.(2)")
                                #        validationBlockChain = False
                                #else:
                                #    headers["Error"] = str("Can't confirm validity state of the registered token.(1)")
                                #    validationBlockChain = False

                                headers["Error"] = str("Can't confirm validity state of the registered token.")
                                validationBlockChain = False
                            else:
                                stateValue = json.loads(strDataGET)["state"]

                                if (stateValue==1):
                                    validationBlockChain = True
                                else:
                                    isRevoked = True
                                    validationBlockChain = False

                        else:
                            headers["Error"] = str("Can't confirm validity state of the registered token.(0)")
                            validationBlockChain = False

                        milli_secBC2=int(round(time.time() * 1000))

                    else:
                        validationBlockChain = True

                break

    except Exception as e:
        logging.info(e)

        headers["Error"] = str(e)

    if (validationCapabilityToken and validationBlockChain):
        validationResult = True

    if (isRevoked):
        strRevoked = " - Code: REVOKED"
    else:
        if (blockchain_usevalidation == 0):
            strRevoked = " - Validation no configured (always true)."

    if headers.get("Error"):
        logging.info("Error: " + str(headers["Error"]))

    logging.info("CAPABILITY TOKEN'S VALIDATION:\n" +
                tabLoggingString + "1) Request... - Result: " + str(validationCapabilityToken) + " - Code: " + str(outTypeProcessed) + "\n" +
                tabLoggingString + "2) BlockChain - Result: " + str(validationBlockChain) + strRevoked + "\n" +
                tabLoggingString + "SUCCESS : Capability token's validation response - " + str(validationResult).upper()
    )

    milli_secValCTT2=int(round(time.time() * 1000))

    if(logginKPI.upper()=="Y".upper()):
        logging.info("")
        logging.info("")
        logging.info("Total(ms) Validacion CT: " + str(milli_secValCT2 - milli_secValCT))
        logging.info("Total(ms) BlockChain: " + str(milli_secBC2 - milli_secBC))
        logging.info("Total(ms) Validacion process: " + str(milli_secValCTT2 - milli_secValCTT))

    return validationResult


def obtainAuthorizationJWT():

    global fed4iotmc_JWT

    headers = {}

    validationJWT = False
    validationResult = False

    milli_secValTestJWTIni=0
    milli_secValTestJWTEnd=0

    milli_secValObtainJWTIni=0
    milli_secValPbtainJWTEnd=0

    milli_secValJWTIni=0
    milli_secValJWTEnd=0

    try:

        logging.info("")
        logging.info("")
        logging.info("Master-Controller JWT'S VALIDATION:")

        milli_secValJWTIni=int(round(time.time() * 1000))

        recoverJWT = True

        if (len(fed4iotmc_JWT)>0):

            recoverJWT = False

            milli_secValTestJWTIni=int(round(time.time() * 1000))

            #Send requests to Master Controler to obtain if it using JWT token has authorisation 
            resultGet = MasterControllerConnection("GET", fed4iotmc_authz_testpath, 
                                                    {"Accept": "application/json", "Authorization": "Bearer "+fed4iotmc_JWT}, None)
            
            try:

                if(resultGet==-1):
                    #If error occurs: need to recover a new JWT token.
                    recoverJWT = True

            except:
                recoverJWT = False

            if ( recoverJWT == False ):

                if (resultGet.code!=200):
                    #If hasn't authorisation: need to recover a new JWT token.
                    recoverJWT = True
                else:
                    #JWT token of fed4iotmc_JWT is valid
                    recoverJWT = False 
                    validationJWT = True

            milli_secValTestJWTEnd=int(round(time.time() * 1000))

        # If need to recover a new JWT token.

        if ( recoverJWT ):

            milli_secValObtainJWTIni=int(round(time.time() * 1000))

            #If JWT doesn't exist or haven't access, send requests to obtain a new one.
            resultPost = MasterControllerConnection("POST", fed4iotmc_login_path, 
                                        {"Content-Type": "application/json"},
                                        "{\"userID\":\"" + fed4iotmc_login_userID + "\",\"password\":\"" + fed4iotmc_login_password + "\"}")

            errorMasterControllerConnectionPOST = False
            try:
                if(resultPost==-1):
                    errorMasterControllerConnectionPOST = True
            except:
                errorMasterControllerConnectionPOST = False

            if (errorMasterControllerConnectionPOST==False):

                strDataPOST = resultPost.read(chunk_size).decode('utf8')

                if (resultPost.code==200):
                    
                    #Obtaion the new JWT from body response.
                    bodyJSON = json.loads(strDataPOST.replace("'", '"'))

                    fed4iotmc_JWT = bodyJSON["access_token"]

                    validationJWT = True

                    logging.info("New JWT Token: " + str(fed4iotmc_JWT))


                else:
                    headers["Error"] = str("Can't obtain JWT token from Master-Controller.(2)")
            else:
                headers["Error"] = str("Can't obtain JWT token from Master-Controller.(1)")

            milli_secValPbtainJWTEnd=int(round(time.time() * 1000))

    except Exception as e:
        logging.info(e)
        headers["Error"] = str(e)


    milli_secValJWTEnd=int(round(time.time() * 1000))

    if (validationJWT):
        validationResult = True

    if headers.get("Error"):
        logging.info("Error: " + str(headers["Error"]))

    logging.info("")
    logging.info("SUCCESS : Master-Controller JWT's validation response - " + str(validationResult).upper())

    if(logginKPI.upper()=="Y".upper()):
        logging.info("")
        logging.info("")
        logging.info("Total(ms) Test JWT: " + str(milli_secValTestJWTEnd - milli_secValTestJWTIni))
        logging.info("Total(ms) Obtain new JWT: " + str(milli_secValPbtainJWTEnd - milli_secValObtainJWTIni))
        logging.info("Total(ms) Validacion process: " + str(milli_secValJWTEnd - milli_secValJWTIni))

    return validationResult
    
def obtainResponseHeaders(ResponseHeaders):

    #logging.info ("********* HEADERS BEFORE obtainResponseHeaders *********")
    #logging.info (ResponseHeaders)


    headers = dict()

    target_chunkedResponse = False

    try:
        for key in ResponseHeaders:
            #logging.info(str(key) + ":" + str(ResponseHeaders[key]))

            if(key.upper()=="Transfer-Encoding".upper() and ResponseHeaders[key].upper()=="chunked".upper()):
                target_chunkedResponse = True

            if(key.upper()!="Date".upper() and key.upper()!="Server".upper()):
                headers[key] = ResponseHeaders[key]
                
    except Exception as e:

        headers["Error"] = str(e)

    #logging.info ("********* HEADERS AFTER obtainResponseHeaders *********")
    #logging.info (headers)

    return  headers, target_chunkedResponse

def loggingPEPRequest(req):
    logging.info("")
    #logging.info (" ********* PEP-REQUEST ********* ")
    #logging.info(req.address_string())
    #logging.info(req.date_time_string())
    #logging.info(req.path)
    #logging.info(req.protocol_version)
    #logging.info(req.raw_requestline)
    logging.info("******* PEP-REQUEST : " + req.address_string() + " - " + str(req.raw_requestline) + " *******")  

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):

    def do_HandleError(self,method,code,title,details):
        messageBody = UtilsPEP.obtainErrorResponseBody(APIVersion,method,code,title,details)
        #code = UtilsPEP.obtainErrorResponseCode(APIVersion,method)
        #self.send_response(code)

        self.send_response(code)

        errorHeaders,chunkedResponse = UtilsPEP.obtainErrorResponseHeaders(APIVersion)
        for key in errorHeaders:
            self.send_header(key, errorHeaders[key])
        self.end_headers() 
        #data = json.dumps(message).encode()
        data = json.dumps(messageBody).encode()
        if(chunkedResponse):
            self.wfile.write(b"%X\r\n%s\r\n" % (len(data), data))
        else:
            self.wfile.write(data)

        self.close_connection

    def do_GET(self):

        target_chunkedResponse=False
        if (self.path=="" or self.path=="/"):
            #To CI/CD.
            self.send_response(200)
            self.end_headers()
            self.close_connection
        else:
            try:
                loggingPEPRequest(self)

                headers,content_length = obtainRequestHeaders(self.headers)

                try:
                    #To find only admittable headers from request previously configured in config.cfg file.
                    value_index = headers.index("Error")
                except:
                    value_index = -1

                testSupported = UtilsPEP.validateNotSupportedMethodPath(APIVersion,self.command,self.path)

                if (value_index != -1):
                    logging.info("Error: " + str(headers["Error"]))
                    SimpleHTTPRequestHandler.do_HandleError(self,self.command,400,"Bad Request","Error obtaining headers.")

                else:

                    if (testSupported == False):
                        logging.info("Error: " + str(headers["Error"]))
                        SimpleHTTPRequestHandler.do_HandleError(self,self.command,501,"Not Implemented","No supported method/path.")

                    else:

                        validation = validationToken(headers,self.command,self.path)

                        if (validation == False):
                            SimpleHTTPRequestHandler.do_HandleError(self,self.command,401,"Unauthorized","The token is missing or invalid.")

                        else:
                     
                            validationMC = obtainAuthorizationJWT()

                            if (validationMC == False):
                                SimpleHTTPRequestHandler.do_HandleError(self,self.command,401,"Unauthorized","The JWT token is missing or invalid.")

                            else:

                                # We are sending this to the CB
                                result = CBConnection(self.command, self.path, headers, None)

                                errorCBConnection = False
                                try:
                                    if(result==-1):
                                        errorCBConnection = True
                                except:
                                    errorCBConnection = False

                                if(errorCBConnection):
                                    SimpleHTTPRequestHandler.do_HandleError(self,self.command,500,"Internal Server Error","GENERAL")
                                else:

                                    # We send back the response to the client
                                    self.send_response(result.code)

                                    headersResponse, target_chunkedResponse = obtainResponseHeaders(result.headers)

                                    #logging.info(" ******* Sending Headers back to client ******* ")
                                    for key in headersResponse:
                                        self.send_header(key, headersResponse[key])

                                    self.end_headers()

                                    #logging.info("Sending the Body back to client")

                                    # Link to resolve Transfer-Encoding chunked cases
                                    # https://docs.amazonaws.cn/en_us/polly/latest/dg/example-Python-server-code.html

                                    while True:
                                        data = result.read(chunk_size)
                                
                                        if (target_chunkedResponse):
                                            self.wfile.write(b"%X\r\n%s\r\n" % (len(data), data))
                                        else:
                                            self.wfile.write(data)
                                        
                                        if data is None or len(data) == 0:
                                            break

                                    if (target_chunkedResponse):
                                        self.wfile.flush()

                                self.close_connection

            except Exception as e:
                logging.info(str(e))
                SimpleHTTPRequestHandler.do_HandleError(self,self.command,500,"Internal Server Error","GENERAL")
        

    def do_POST(self):
        target_chunkedResponse=False

        try:

            loggingPEPRequest(self)

            headers,content_length = obtainRequestHeaders(self.headers)

            try:
                #To find only admittable headers from request previously configured in config.cfg file.
                value_index = headers.index("Error")
            except:
                value_index = -1

            testSupported = UtilsPEP.validateNotSupportedMethodPath(APIVersion,self.command,self.path)

            if (value_index != -1):
                logging.info("Error: " + str(headers["Error"]))
                SimpleHTTPRequestHandler.do_HandleError(self,self.command,400,"Bad Request","Error obtaining headers.")

            else:

                if (testSupported == False):
                    logging.info("Error: " + str(headers["Error"]))
                    SimpleHTTPRequestHandler.do_HandleError(self,self.command,501,"Not Implemented","No supported method/path.")

                else:

                    #logging.info (" ********* OBTAIN BODY ********* ")
                    # We get the body
                    if (content_length>0):
                        #logging.info ("-------- self.rfile.read(content_length) -------")
                        post_body   = self.rfile.read(content_length)
                    else:
                        #logging.info ("-------- Lanzo self.rfile.read() -------")
                        post_body   = self.rfile.read()

                    #logging.info(post_body)

                    validation = validationToken(headers,self.command,self.path,post_body)

                    if (validation == False):
                        SimpleHTTPRequestHandler.do_HandleError(self,self.command,401,"Unauthorized","The token is missing or invalid.")

                    else:

                        validationMC = obtainAuthorizationJWT()

                        if (validationMC == False):
                            SimpleHTTPRequestHandler.do_HandleError(self,self.command,401,"Unauthorized","The JWT token is missing or invalid.")

                        else:

                            # We are sending this to the CB
                            result = CBConnection(self.command, self.path,headers, post_body)

                            errorCBConnection = False
                            try:
                                if(result==-1):
                                    errorCBConnection = True
                            except:
                                errorCBConnection = False

                            if(errorCBConnection):
                                SimpleHTTPRequestHandler.do_HandleError(self,self.command,500,"Internal Server Error","GENERAL")
                            else:

                                # We send back the response to the client
                                self.send_response(result.code)

                                headersResponse, target_chunkedResponse = obtainResponseHeaders(result.headers)

                                #logging.info(" ******* Sending Headers back to client ******* ")
                                for key in headersResponse:
                                    self.send_header(key, headersResponse[key])

                                self.end_headers()

                                #logging.info("Sending the Body back to client")

                                # Link to resolve Transfer-Encoding chunked cases
                                # https://docs.amazonaws.cn/en_us/polly/latest/dg/example-Python-server-code.html

                                while True:
                                    data = result.read(chunk_size)
                            
                                    if (target_chunkedResponse):
                                        self.wfile.write(b"%X\r\n%s\r\n" % (len(data), data))
                                    else:
                                        self.wfile.write(data)

                                    if data is None or len(data) == 0:
                                        break

                                if (target_chunkedResponse):
                                    self.wfile.flush()

                            self.close_connection

        except Exception as e:
            logging.info(str(e))
            SimpleHTTPRequestHandler.do_HandleError(self,self.command,500,"Internal Server Error","GENERAL")

    def do_DELETE(self):
        target_chunkedResponse=False

        try:
            
            loggingPEPRequest(self)

            headers,content_length = obtainRequestHeaders(self.headers)

            try:
                #To find only admittable headers from request previously configured in config.cfg file.
                value_index = headers.index("Error")
            except:
                value_index = -1

            testSupported = UtilsPEP.validateNotSupportedMethodPath(APIVersion,self.command,self.path)

            if (value_index != -1):
                logging.info("Error: " + str(headers["Error"]))
                SimpleHTTPRequestHandler.do_HandleError(self,self.command,400,"Bad Request","Error obtaining headers.")

            else:

                if (testSupported == False):
                    logging.info("Error: " + str(headers["Error"]))
                    SimpleHTTPRequestHandler.do_HandleError(self,self.command,501,"Not Implemented","No supported method/path.")

                else:

                    validation = validationToken(headers,self.command,self.path)

                    if (validation == False):
                        SimpleHTTPRequestHandler.do_HandleError(self,self.command,401,"Unauthorized","The token is missing or invalid.")

                    else:

                        validationMC = obtainAuthorizationJWT()

                        if (validationMC == False):
                            SimpleHTTPRequestHandler.do_HandleError(self,self.command,401,"Unauthorized","The JWT token is missing or invalid.")

                        else:

                            # We are sending this to the CB
                            result = CBConnection(self.command, self.path, headers, None)

                            errorCBConnection = False
                            try:
                                if(result==-1):
                                    errorCBConnection = True
                            except:
                                errorCBConnection = False

                            if(errorCBConnection):
                                SimpleHTTPRequestHandler.do_HandleError(self,self.command,500,"Internal Server Error","GENERAL")
                            else:        
                                # We send back the response to the client
                                self.send_response(result.code)

                                headersResponse, target_chunkedResponse = obtainResponseHeaders(result.headers)

                                #logging.info(" ******* Sending Headers back to client ******* ")
                                for key in headersResponse:
                                    self.send_header(key, headersResponse[key])

                                self.end_headers()

                                #logging.info("Sending the Body back to client")

                                # Link to resolve Transfer-Encoding chunked cases
                                # https://docs.amazonaws.cn/en_us/polly/latest/dg/example-Python-server-code.html

                                while True:
                                    data = result.read(chunk_size)
                            
                                    if (target_chunkedResponse):
                                        self.wfile.write(b"%X\r\n%s\r\n" % (len(data), data))
                                    else:
                                        self.wfile.write(data)

                                    if data is None or len(data) == 0:
                                        break

                                if (target_chunkedResponse):
                                    self.wfile.flush()

                            self.close_connection

        except Exception as e:
            logging.info(str(e))
            SimpleHTTPRequestHandler.do_HandleError(self,self.command,500,"Internal Server Error","GENERAL")

    def do_PATCH(self):
        target_chunkedResponse=False

        try:

            loggingPEPRequest(self)

            headers,content_length = obtainRequestHeaders(self.headers)

            try:
                #To find only admittable headers from request previously configured in config.cfg file.
                value_index = headers.index("Error")
            except:
                value_index = -1

            testSupported = UtilsPEP.validateNotSupportedMethodPath(APIVersion,self.command,self.path)


            if (value_index != -1):
                logging.info("Error: " + str(headers["Error"]))
                SimpleHTTPRequestHandler.do_HandleError(self,self.command,400,"Bad Request","Error obtaining headers.")

            else:

                if (testSupported == False):
                    logging.info("Error: " + str(headers["Error"]))
                    SimpleHTTPRequestHandler.do_HandleError(self,self.command,501,"Not Implemented","No supported method/path.")

                else:

                    #logging.info (" ********* OBTAIN BODY ********* ")
                    # We get the body
                    if (content_length>0):
                        #logging.info ("-------- self.rfile.read(content_length) -------")
                        patch_body   = self.rfile.read(content_length)
                    else:
                        #logging.info ("-------- Lanzo self.rfile.read() -------")
                        patch_body   = self.rfile.read()

                    #logging.info(patch_body)

                    validation = validationToken(headers,self.command,self.path,patch_body)

                    if (validation == False):
                        SimpleHTTPRequestHandler.do_HandleError(self,self.command,401,"Unauthorized","The token is missing or invalid.")

                    else:

                        validationMC = obtainAuthorizationJWT()

                        if (validationMC == False):
                            SimpleHTTPRequestHandler.do_HandleError(self,self.command,401,"Unauthorized","The JWT token is missing or invalid.")

                        else:

                            # We are sending this to the CB
                            result = CBConnection(self.command, self.path,headers, patch_body)

                            errorCBConnection = False
                            try:
                                if(result==-1):
                                    errorCBConnection = True
                            except:
                                errorCBConnection = False

                            if(errorCBConnection):
                                SimpleHTTPRequestHandler.do_HandleError(self,self.command,500,"Internal Server Error","GENERAL")
                            else:        
                                # We send back the response to the client
                                self.send_response(result.code)

                                headersResponse, target_chunkedResponse = obtainResponseHeaders(result.headers)

                                #logging.info(" ******* Sending Headers back to client ******* ")
                                for key in headersResponse:
                                    self.send_header(key, headersResponse[key])

                                self.end_headers()

                                logging.info("Sending the Body back to client")

                                # Link to resolve Transfer-Encoding chunked cases
                                # https://docs.amazonaws.cn/en_us/polly/latest/dg/example-Python-server-code.html

                                while True:
                                    data = result.read(chunk_size)
                            
                                    if (target_chunkedResponse):
                                        self.wfile.write(b"%X\r\n%s\r\n" % (len(data), data))
                                    else:
                                        self.wfile.write(data)

                                    if data is None or len(data) == 0:
                                        break

                                if (target_chunkedResponse):
                                    self.wfile.flush()

                            self.close_connection

        except Exception as e:
            logging.info(str(e))
            SimpleHTTPRequestHandler.do_HandleError(self,self.command,500,"Internal Server Error","GENERAL")            
            

    ##Actually not suppported
    def do_PUT(self):
        #SimpleHTTPRequestHandler.do_HandleError(self,self.command,501,"Not Implemented","No supported method.")

        target_chunkedResponse=False

        try:

            loggingPEPRequest(self)

            headers,content_length = obtainRequestHeaders(self.headers)

            try:
                #To find only admittable headers from request previously configured in config.cfg file.
                value_index = headers.index("Error")
            except:
                value_index = -1

            testSupported = UtilsPEP.validateNotSupportedMethodPath(APIVersion,self.command,self.path)


            if (value_index != -1):
                logging.info("Error: " + str(headers["Error"]))
                SimpleHTTPRequestHandler.do_HandleError(self,self.command,400,"Bad Request","Error obtaining headers.")

            else:

                if (testSupported == False):
                    logging.info("Error: " + str(headers["Error"]))
                    SimpleHTTPRequestHandler.do_HandleError(self,self.command,501,"Not Implemented","No supported method/path.")

                else:

                    put_body = None

                    try:

                        #logging.info (" ********* OBTAIN BODY ********* ")
                        # We get the body
                        if (content_length>0):
                            #logging.info ("-------- self.rfile.read(content_length) -------")
                            put_body   = self.rfile.read(content_length)
                        else:
                            #logging.info ("-------- Lanzo self.rfile.read() -------")
                            put_body   = self.rfile.read()
                        
                        #logging.info(put_body)

                    except:
                        put_body = None

                    validation = validationToken(headers,self.command,self.path,put_body)

                    if (validation == False):
                        SimpleHTTPRequestHandler.do_HandleError(self,self.command,401,"Unauthorized","The token is missing or invalid.")

                    else:

                        validationMC = obtainAuthorizationJWT()

                        if (validationMC == False):
                            SimpleHTTPRequestHandler.do_HandleError(self,self.command,401,"Unauthorized","The JWT token is missing or invalid.")

                        else:

                            # We are sending this to the CB
                            result = CBConnection(self.command, self.path,headers, put_body)

                            errorCBConnection = False
                            try:
                                if(result==-1):
                                    errorCBConnection = True
                            except:
                                errorCBConnection = False

                            if(errorCBConnection):
                                SimpleHTTPRequestHandler.do_HandleError(self,self.command,500,"Internal Server Error","GENERAL")
                            else:        
                                # We send back the response to the client
                                self.send_response(result.code)

                                headersResponse, target_chunkedResponse = obtainResponseHeaders(result.headers)

                                #logging.info(" ******* Sending Headers back to client ******* ")
                                for key in headersResponse:
                                    self.send_header(key, headersResponse[key])

                                self.end_headers()

                                #logging.info("Sending the Body back to client")

                                # Link to resolve Transfer-Encoding chunked cases
                                # https://docs.amazonaws.cn/en_us/polly/latest/dg/example-Python-server-code.html

                                while True:
                                    data = result.read(chunk_size)
                            
                                    if (target_chunkedResponse):
                                        self.wfile.write(b"%X\r\n%s\r\n" % (len(data), data))
                                    else:
                                        self.wfile.write(data)
                                    
                                    if data is None or len(data) == 0:
                                        break
                        
                                if (target_chunkedResponse):
                                    self.wfile.flush()

                            self.close_connection

        except Exception as e:
            logging.info(str(e))
            SimpleHTTPRequestHandler.do_HandleError(self,self.command,500,"Internal Server Error","GENERAL")

logPath="./"
fileName="out"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s",
    handlers=[
        logging.FileHandler("{0}/{1}.log".format(logPath, fileName)),
        logging.StreamHandler(sys.stdout)
    ])

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
            """Handle requests in a separate thread."""

if __name__ == '__main__':

    httpd = ThreadedHTTPServer( (pep_host, pep_port), SimpleHTTPRequestHandler )

    if (pep_protocol.upper() == "https".upper()) :
        httpd.socket = ssl.wrap_socket (httpd.socket,
            keyfile="./certs/server-priv-rsa.pem",
            certfile="./certs/server-public-cert.pem",
            server_side = True,
            ssl_version=ssl.PROTOCOL_TLS
        )

    httpd.serve_forever()

#httpd = HTTPServer( (pep_host, pep_port), SimpleHTTPRequestHandler )
#
#httpd.socket = ssl.wrap_socket (httpd.socket,
#        keyfile="certs/server-priv-rsa.pem",
#        certfile='certs/server-public-cert.pem',
#        server_side = True)
#
#httpd.serve_forever()
