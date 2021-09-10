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
from subprocess import Popen, PIPE
import html
import os
from socketserver import ThreadingMixIn
import threading

import time

#Obtain configuracion from config.cfg file.
cfg = configparser.ConfigParser()  
cfg.read(["./config.cfg"])  
host = cfg.get("GENERAL", "host")
port = int(cfg.get("GENERAL", "port"))
chunk_size=int(cfg.get("GENERAL", "chunk_size"))

#keyrock_protocol = cfg.get("GENERAL", "keyrock_protocol")
#keyrock_host = cfg.get("GENERAL", "keyrock_host")
#keyrock_port = cfg.get("GENERAL", "keyrock_port")

keyrock_protocol = str(os.getenv('keyrock_protocol'))
keyrock_host = str(os.getenv('keyrock_host'))
keyrock_port = int(os.getenv('keyrock_port'))
keyrock_admin_email=str(os.getenv('keyrock_admin_email'))
keyrock_admin_pass=str(os.getenv('keyrock_admin_pass'))

blockchain_usevalidation = int(os.getenv('blockchain_usevalidation'))
blockchain_protocol = str(os.getenv('blockchain_protocol'))
blockchain_host = str(os.getenv('blockchain_host'))
blockchain_port = int(os.getenv('blockchain_port'))

pdp_url = str(os.getenv('PDP_URL'))

try:
    capman_protocol = str(os.getenv('capman_protocol'))
except Exception as e:
    logging.info(e)
    capman_protocol = "https"

if (str(capman_protocol).upper() == "None".upper()) :
    capman_protocol = "https"

tabLoggingString = "\t\t\t\t\t\t\t"

logginKPI = cfg.get("GENERAL", "logginKPI")

gcontext = ssl.SSLContext()

def getstatusoutput(command):

    milli_secGenCT=int(round(time.time() * 1000))

    process = Popen(command, stdout=PIPE,stderr=PIPE)
    out, err = process.communicate()

    milli_secGenCT2=int(round(time.time() * 1000))


    if(logginKPI.upper()=="Y".upper()):
        logging.info("Total(ms) CT Generator: " + str(milli_secGenCT2 - milli_secGenCT))

    #print("out")
    #print(out)
    #print("err")
    #print(err)

    return (process.returncode, out)

def obtainRequestHeaders(RequestHeaders):

    headers = dict()

    content_length = 0

    try:
        # We get the headers
        
        #logging.info (" ********* HEADERS BEFORE obtainRequestHeaders ********* ")
        #logging.info (RequestHeaders)
        
        for key in RequestHeaders:
            #logging.info("Procesando: " + str(key) + ":" + str(RequestHeaders[key]))

            value_index=-1

            try:
                #To find only admittable headers from request previously configured in config.cfg file.
                value_index = apiHeaders.index(key.lower())

            except:
                value_index = -1

            #If the header key was found, it will be considered after.
            if (value_index > -1 ):

                #logging.info("Incluido: " + str(key) + ":" + str(RequestHeaders[key]))

                headers[key] = RequestHeaders[key]

            if(key.upper()=="Content-Length".upper()):
                content_length = int(RequestHeaders[key])

    except Exception as e:
        logging.info(e)

        headers["Error"] = str(e)

    #logging.info (" ********* HEADERS AFTER obtainRequestHeaders ********* ")
    #logging.info (headers)

    return headers, content_length

def generateToken(subjectType, subject, action, device, resource):

    #validation = False

    outTypeProcessed = ""

    cmToken=""

    try:

        #logging.info("subject: " +str(subject))
        #logging.info("action: " +str(action))
        #logging.info("device: " +str(device))
        #logging.info("resource: " +str(resource))
        #logging.info("pdp: " +str(pdp_url))

        #Validating token : 
        #Observation: str(resource).replace("&",";") --> for PDP error: "The reference to entity "***" must end with the ';' delimiter.""
        codeType, outType = getstatusoutput(["java","-jar","CapabilityGenerator.jar",
            str(subjectType),
            str(subject),
            str(action),
            str(device),
            str(resource).replace("&",";"),
            str(pdp_url)
            ])
        #logging.info("subject: " +str(subject))
        #logging.info("action: " +str(action))
        #logging.info("device: " +str(device))
        #logging.info("resource: " +str(resource))

        #logging.info("GENERATE CAPABILITY TOKEN - Response:\n" + str(outType))

        outTypeProcessed = json.loads(outType.decode('utf8').replace("'", '"').replace("*****generateSignature: \n","").replace("\n", ""))
        #outTypeProcessed = outType.decode('utf8').replace("'", '"').replace("CODE: ","")

        #logging.info("generateToken - outTypeProcessed: " + str(outTypeProcessed))

        #logging.info("outTypeProcessed")
        #logging.info(outTypeProcessed)
        #logging.info(type(outTypeProcessed))

        #if(outTypeProcessed["code"]=="ok"):
        #    cmToken = outTypeProcessed["capabilityToken"]
        #else:
        #    cmToken = {"error": "error"}

        if ("code" in outTypeProcessed):
            if(outTypeProcessed["code"]=="ok"):
                cmToken = outTypeProcessed["capabilityToken"]
            else:
                cmToken = {"error": "error"}
        elif ("su"  in outTypeProcessed and "de" in outTypeProcessed):
            if(outTypeProcessed["su"]==str(subject) and outTypeProcessed["de"]==str(device)):
                cmToken = outTypeProcessed
            else:
                cmToken = {"error": "error"}  
        else: 
            cmToken = {"error": "error"}

    except Exception as e:
        logging.info(e)

        cmToken = {"error": "error"}

#    logging.info ("validationToken - Result: " + str(validation) + " - Code: " + str(outTypeProcessed))

    return cmToken

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

def loggingRequest(req):
    logging.info("")
    #logging.info (" ********* PEP-REQUEST ********* ")
    #logging.info(req.address_string())
    #logging.info(req.date_time_string())
    #logging.info(req.path)
    #logging.info(req.protocol_version)
    #logging.info(req.raw_requestline)
    logging.info(" ******* NEW CAPABILITY TOKEN - Request : " + req.address_string() + " - " + str(req.raw_requestline) + " ******* ")  

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_HandleError(self,method):
        self.send_response(500)
        self.end_headers() 
        data = json.dumps("Internal server error").encode()

        self.wfile.write(data)

        self.close_connection
    
    def do_POST(self):
        try:

            #loggingRequest(self)

            logging.info("******* NEW CAPABILITY TOKEN REQUEST : " + self.address_string() + " *******")  

            headers,content_length = obtainRequestHeaders(self.headers)

            try:
                #To find only admittable headers from request previously configured in config.cfg file.
                value_index = apiHeaders.index("Error")
            except:
                value_index = -1

            if (value_index != -1):
                logging.info("Error: " + str(headers["Error"]))
                SimpleHTTPRequestHandler.do_HandleError(self,"POST")
                    
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

                #Convert from byte to JSON (dict)
                bodyJSON = json.loads(post_body.decode('utf8').replace("'", '"'))

                token = bodyJSON["token"]
                deValue = bodyJSON["de"]
                acValue = bodyJSON["ac"]
                reValue = bodyJSON["re"]
                
                logging.info("Step 1) Obtaining Keyrock Token info ...")

                headers = {"X-Auth-token": token, 
                        "X-Subject-token": token}

                if(keyrock_protocol.upper()=="http".upper()):
                    conn = http.client.HTTPConnection(keyrock_host,keyrock_port)
                else:
                    #conn = http.client.HTTPSConnection(keyrock_host,keyrock_port,
                    #                                key_file="./certs/idm-2018-key.pem",
                    #                                cert_file="./certs/idm-2018-cert.pem",
                    #                                context=gcontext)
                    conn = http.client.HTTPSConnection(keyrock_host,keyrock_port,
                                                context=gcontext)

                conn.request("GET", "/v1/auth/tokens", None, headers)
                response = conn.getresponse()

                status = response.status
                reason = response.reason
                data = response.read()
                conn.close()

                if(status==200):

                    bodyJSON = json.loads(data.decode('utf8').replace("'", '"'))

                    logging.info("Keyrock Token info response : " + str(bodyJSON))

                    validToken = bodyJSON["valid"]

                    userEnabled = bodyJSON["User"]["enabled"]

                    if (validToken == False or userEnabled == False):
                        logging.info("Obtaining Keyrock Token info response : Error.")
                        
                        #self.send_response(500)
                        #self.end_headers()
                        #
                        #if(validToken == False):
                        #    self.wfile.write(json.dumps("Invalid token.").encode())
                        #else
                        #    self.wfile.write(json.dumps("User disabled.").encode())

                        self.send_response(401)
                        self.end_headers()
                        
                        message = {"error": { "message": "Invalid email or password", "code": 401, "title": "Unauthorized" } }

                        if(validToken == False):
                            message["error"]["message"] =  "Invalid token."
                        
                        logging.info(str(message))

                        self.wfile.write(json.dumps(message).encode())

                    else:

                        idUser = bodyJSON["User"]["id"]

                        cmToken = {"error": "error"}

                        #Obtain the keyrock admin user token, required to access to the roles...
                        headers = {"Content-Type":"application/json"}   
                        body = json.dumps({"name":keyrock_admin_email,"password":keyrock_admin_pass}).encode()

                        keyRockMethod="POST"
                        keyRockUri="/v1/auth/tokens"

                        if(keyrock_protocol.upper()=="http".upper()):
                            conn = http.client.HTTPConnection(keyrock_host,keyrock_port)
                        else:
                            #conn = http.client.HTTPSConnection(keyrock_host,keyrock_port,
                            #                                key_file="./certs/idm-2018-key.pem",
                            #                                cert_file="./certs/idm-2018-cert.pem",
                            #                                context=gcontext)
                            conn = http.client.HTTPSConnection(keyrock_host,keyrock_port,
                                                        context=gcontext)

                        conn.request("POST", "/v1/auth/tokens", body, headers)
                        response = conn.getresponse()

                        status = response.status
                        reason = response.reason
                        data = response.read()
                        conn.close()

                        if(status==201):

                            keyRockTokenAdmin = response.headers["X-Subject-Token"]

                            #Obtain the keyrock aplication list where user is contained
                            headers = {"X-Auth-token": token}

                            if(keyrock_protocol.upper()=="http".upper()):
                                conn = http.client.HTTPConnection(keyrock_host,keyrock_port)
                            else:
                                #conn = http.client.HTTPSConnection(keyrock_host,keyrock_port,
                                #                                key_file="./certs/idm-2018-key.pem",
                                #                                cert_file="./certs/idm-2018-cert.pem",
                                #                                context=gcontext)
                                conn = http.client.HTTPSConnection(keyrock_host,keyrock_port,
                                                            context=gcontext)

                            conn.request("GET", "/v1/applications", None, headers)
                            response = conn.getresponse()

                            status = response.status
                            reason = response.reason
                            data = response.read()
                            conn.close()

                            if(status==200):

                                bodyJSON = json.loads(data.decode('utf8').replace("'", '"'))

                                applicationList = bodyJSON["applications"]

                                for application in applicationList:

                                    idApplication = application["id"]

                                    #Obtain the keyrock aplication user role
                                    headers = {"X-Auth-token": keyRockTokenAdmin}

                                    if(keyrock_protocol.upper()=="http".upper()):
                                        conn = http.client.HTTPConnection(keyrock_host,keyrock_port)
                                    else:
                                        #conn = http.client.HTTPSConnection(keyrock_host,keyrock_port,
                                        #                                key_file="./certs/idm-2018-key.pem",
                                        #                                cert_file="./certs/idm-2018-cert.pem",
                                        #                                context=gcontext)
                                        conn = http.client.HTTPSConnection(keyrock_host,keyrock_port,
                                                                    context=gcontext)

                                    conn.request("GET", "/v1/applications/" + idApplication + "/users/" + idUser + "/roles", None, headers)
                                    response = conn.getresponse()

                                    status = response.status
                                    reason = response.reason
                                    data = response.read()
                                    conn.close()

                                    if(status==200):

                                        bodyJSON = json.loads(data.decode('utf8').replace("'", '"'))

                                        roleList = bodyJSON["role_user_assignments"]
                                        
                                        for role in roleList:

                                            roleID = role["role_id"]
                                            
                                            logging.info("Step 2) Obtaining capability token to 'urn:oasis:names:tc:xacml:2.0:subject:applicationrole':\n" +
                                                "{\n" + 
                                                "\t\tsu: " + idApplication + "_" + roleID + " (" + application["id"] +  "),\n" +
                                                "\t\tde: " + deValue + ",\n" +
                                                "\t\tac: " + acValue + ",\n" +
                                                "\t\tre: " + reValue + "\n" +
                                                "}")

                                            cmToken = generateToken("urn:oasis:names:tc:xacml:2.0:subject:applicationrole", 
                                                                    idApplication + "_" + roleID, 
                                                                    acValue, deValue, reValue)

                                            # If capability token is created, it finishes.
                                            if 'error' not in cmToken:
                                                break

                                    # If capability token is created, it finishes.
                                    if 'error' not in cmToken:
                                        break

                        else:

                            logging.info("Capability Manager, can't access to applications & roles of IdM")

                        #If capability token is not obtained from application/roles, it accesses to organizations and try to obtain it with them... 
                        if 'error' in cmToken:

                            #Obtain the keyrock organization list where user is contained
                            headers = {"X-Auth-token": token}

                            if(keyrock_protocol.upper()=="http".upper()):
                                conn = http.client.HTTPConnection(keyrock_host,keyrock_port)
                            else:
                                #conn = http.client.HTTPSConnection(keyrock_host,keyrock_port,
                                #                                key_file="./certs/idm-2018-key.pem",
                                #                                cert_file="./certs/idm-2018-cert.pem",
                                #                                context=gcontext)
                                conn = http.client.HTTPSConnection(keyrock_host,keyrock_port,
                                                                    context=gcontext)

                            conn.request("GET", "/v1/organizations", None, headers)
                            response = conn.getresponse()

                            status = response.status
                            reason = response.reason
                            data = response.read()
                            conn.close()

                            if(status==200):
                                bodyJSON = json.loads(data.decode('utf8').replace("'", '"'))

                                '''
                                    {
                                        "organizations": [
                                            {
                                                "role": "member",
                                                "Organization": {
                                                    "id": "d3c69307-8a09-4c50-b7a6-dfde40fab507",
                                                    "name": "Organization 2",
                                                    "description": "Organization 2",
                                                    "image": "default",
                                                    "website": null
                                                }
                                            }
                                        ]
                                    }
                                '''
                                
                                organizationList = bodyJSON["organizations"]

                                # Obtain the organizations where the user is included and try to obtain the capability token, when obtain it stops and returns it, else try 
                                # with the next one.
                                for organization in organizationList:

                                    logging.info("Step 2) Obtaining capability token to 'urn:ietf:params:scim:schemas:core:2.0:organizationname':\n" +
                                                "{\n" + 
                                                "\t\tsu: " + organization["Organization"]["id"] + " (" + organization["Organization"]["name"] +  "),\n" +
                                                "\t\tde: " + deValue + ",\n" +
                                                "\t\tac: " + acValue + ",\n" +
                                                "\t\tre: " + reValue + "\n" +
                                                "}")

                                    cmToken = generateToken("urn:ietf:params:scim:schemas:core:2.0:organizationname", organization["Organization"]["name"], 
                                                            acValue, deValue, reValue)

                                    # If capability token is created, it finishes.
                                    if 'error' not in cmToken:
                                        break

                                    logging.info("Step 2) Obtaining capability token to 'urn:ietf:params:scim:schemas:core:2.0:organization':\n" +
                                                "{\n" + 
                                                "\t\tsu: " + organization["Organization"]["id"] + " (" + organization["Organization"]["name"] +  "),\n" +
                                                "\t\tde: " + deValue + ",\n" +
                                                "\t\tac: " + acValue + ",\n" +
                                                "\t\tre: " + reValue + "\n" +
                                                "}")

                                    cmToken = generateToken("urn:ietf:params:scim:schemas:core:2.0:organization", organization["Organization"]["id"], 
                                                            acValue, deValue, reValue)

                                    # If capability token is created, it finishes.
                                    if 'error' not in cmToken:
                                        break

                        #If capability token is not obtained from organizations, it accesses to the rest of user attributes and try to obtain it with them... 
                        if 'error' in cmToken:

                            #Obtain the keyrock user attributes
                            headers = {"X-Auth-token": token}

                            if(keyrock_protocol.upper()=="http".upper()):
                                conn = http.client.HTTPConnection(keyrock_host,keyrock_port)
                            else:
                                #conn = http.client.HTTPSConnection(keyrock_host,keyrock_port,
                                #                                key_file="./certs/idm-2018-key.pem",
                                #                                cert_file="./certs/idm-2018-cert.pem",
                                #                                context=gcontext)
                                conn = http.client.HTTPSConnection(keyrock_host,keyrock_port,
                                                                context=gcontext)

                            conn.request("GET", "/v1/users/" + idUser, None, headers)
                            response = conn.getresponse()

                            status = response.status
                            reason = response.reason
                            data = response.read()
                            conn.close()

                            if(status==200):

                                bodyJSON = json.loads(data.decode('utf8').replace("'", '"'))

                                '''
                                    For instance:
                                    {
                                        "user": {
                                            "scope": [],
                                            "id": "c669093a-edf0-40eb-b036-0a5faa434d70",
                                            "username": "usuariotres",
                                            "email": "usuariotres@test.com",
                                            "enabled": true,
                                            "admin": false,
                                            "image": "default",
                                            "gravatar": false,
                                            "date_password": "2020-10-08T09:23:50.000Z",
                                            "description": "",
                                            "website": ""
                                        }
                                    }
                                '''

                                idUser = bodyJSON["user"]["id"]
                                usernameValue = bodyJSON["user"]["username"]
                                emailValue =  bodyJSON["user"]["email"]

                                #Actually not used admin,gravatar,description,website to use only descomment and add a new element in subjectList
                                #adminValue = ""
                                #if (bodyJSON["user"]["admin"]):
                                #    adminValue = "admin"
                                #
                                #gravatarValue = ""
                                #if (bodyJSON["user"]["gravatar"]):
                                #    gravatarValue = "gravatar"
                                #
                                #descriptionValue =  bodyJSON["user"]["description"]
                                #websiteValue =  bodyJSON["user"]["website"]
                                
                                #To support a new subjectType you only need to add a new element
                                subjectList=[
                                                ["urn:ietf:params:scim:schemas:core:2.0:username",usernameValue],
                                                ["urn:ietf:params:scim:schemas:core:2.0:email",emailValue],
                                                ["urn:ietf:params:scim:schemas:core:2.0:id",idUser]
                                            ]

                                for i in range(len(subjectList)):

                                    logging.info("Step 2) Obtaining capability token to '"+ subjectList[i][0] +"':\n" +
                                                "{\n" + 
                                                "\t\tsu: " + subjectList[i][1] + ",\n" +
                                                "\t\tde: " + deValue + ",\n" +
                                                "\t\tac: " + acValue + ",\n" +
                                                "\t\tre: " + reValue + "\n" +
                                                "}")

                                    cmToken = generateToken(subjectList[i][0], subjectList[i][1], acValue, deValue, reValue)

                                    # If capability token is created, it finishes.
                                    if 'error' not in cmToken:
                                        break

                        if 'error' not in cmToken:
                            try:
                                # If using integration with blockchain register the Capabiltiy Token Identifier.
                                if (blockchain_usevalidation == 1):
                                    milli_secBC=int(round(time.time() * 1000))

                                    #If Capability Token id don't exist, send requests to register it.
                                    resultPost = BlockChainConnection("POST", "/token/register", {}, "{\"id\":\"" + cmToken["id"] + "\"}")

                                    errorBlockChainConnectionPOST = False
                                    try:
                                        if(resultPost==-1):
                                            errorBlockChainConnectionPOST = True
                                    except:
                                        errorBlockChainConnectionPOST = False

                                    if (errorBlockChainConnectionPOST==False):

                                        strDataPOST = resultPost.read(chunk_size).decode('utf8')

                                        if (resultPost.code!=201):
                                            cmToken = {"error": "error"}
                                    else:
                                        cmToken = {"error": "error"}
                                    
                                    milli_secBC2=int(round(time.time() * 1000))

                                    if(logginKPI.upper()=="Y".upper()):
                                        logging.info("Total(ms) BlockChain token register: " + str(milli_secBC2 - milli_secBC))

                            except Exception as e:
                                logging.info("Error: BlockChain token register: " + str(e))

                                cmToken = {"error": "error"}
                            
                            # We send back the response to the client
                            if 'error' not in cmToken:
                                logging.info("Obtaining capability token response : NEW CAPABILITY TOKEN : " + str(cmToken))
                                self.send_response(200)
                                self.end_headers()
                                self.wfile.write(json.dumps(cmToken).encode())
                            else:
                                logging.info("Obtaining capability token response : Error.")
                                self.send_response(500)
                                self.end_headers()
                                self.wfile.write(json.dumps("Can't generate capability token. Reason: Blockchain error.").encode())
                                
                        else:
                        ## We send back the response to the client
                        #if 'error' not in cmToken:
                        #    logging.info("Obtaining capability token response : NEW CAPABILITY TOKEN : " + str(cmToken))
                        #    self.send_response(200)
                        #    self.end_headers()
                        #    self.wfile.write(json.dumps(cmToken).encode())
                        #else:
                            logging.info("Obtaining capability token response : Error.")
                            self.send_response(500)
                            self.end_headers()
                            self.wfile.write(json.dumps("Can't generate capability token").encode())

                    self.close_connection
                else:
                    logging.info("Obtaining Keyrock Token info response : Error.")
                    logging.info(json.loads(data.decode('utf8').replace("'", '"')))

                    #self.send_response(500)
                    self.send_response(status)
                    self.end_headers()
                    #self.wfile.write(json.dumps("Keyrock Token info response : Token info not found.").encode())
                    self.wfile.write(data)
                    self.close_connection
                
        except Exception as e:
            logging.info(str(e))
            
            SimpleHTTPRequestHandler.do_HandleError(self,"POST")
    
    def do_GET(self):

        logging.info(str(keyrock_protocol))
        logging.info(str(keyrock_host))
        logging.info(str(keyrock_port))

        self.send_response(200)
        self.end_headers()
        self.close_connection

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

    httpd = ThreadedHTTPServer( (host, port), SimpleHTTPRequestHandler )

    if (capman_protocol.upper() == "https".upper()) :
        httpd.socket = ssl.wrap_socket (httpd.socket,
            keyfile="./certs/server-priv-rsa.pem",
            certfile="./certs/server-public-cert.pem",
            server_side = True,
            ssl_version=ssl.PROTOCOL_TLS
        )

    httpd.serve_forever()

#httpd = HTTPServer( (host, port), SimpleHTTPRequestHandler )
#
#httpd.socket = ssl.wrap_socket (httpd.socket,
#        keyfile="certs/server-priv-rsa.pem",
#        certfile="certs/server-public-cert.pem",
#        server_side = True)
#
#httpd.serve_forever()
