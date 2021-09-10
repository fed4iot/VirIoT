#
#Copyright Odin Solutions S.L. All Rights Reserved.
#
#SPDX-License-Identifier: Apache-2.0
#

import http.client

import configparser
import json
from subprocess import Popen, PIPE
import ssl

noEncryptedKeys=["@id","@type","@context"]

def get_chunk_size(resp):
    size_str = resp.read(2)
    if(size_str.decode('utf8').replace("'", '"')==""):
        return 0
    while size_str[-2:] != b"\r\n":
        size_str += resp.read(1)
    return int(size_str[:-2], 16)

def get_chunk_data(resp,chunk_size):
    data = resp.read(chunk_size)
    resp.read(2)
    return data

def getstatusoutput(command):
    process = Popen(command, stdout=PIPE,stderr=PIPE)
    out, err = process.communicate()

    #print("out")
    #print(out)
    #print("err")
    #print(err)

    return (process.returncode, out)

#This process consider ONLY a JSON format.
def decipherBodyAttributes(body):

    bodyBackUp = body

    try:

        for key in body:
            try:

                if(key.lower() not in noEncryptedKeys):
                    #Verify, encriptation type.

                    testEncryptCPABE = False

                    testEncryptCPABE_CASE = False

                    for key2 in body[key]:
                        if (key2 == "https://uri.etsi.org/ngsi-ld/default-context/encrypt_cpabe"):
                            if (body[key][key2]["https://uri.etsi.org/ngsi-ld/hasValue"]=="encrypt_cpabe"):
                                testEncryptCPABE = True
                                testEncryptCPABE_CASE = 1
                                break

                        if (key2 == "encrypt_cpabe"):
                            if (body[key][key2]["value"]=="encrypt_cpabe"):
                                testEncryptCPABE = True
                                testEncryptCPABE_CASE = 2
                                break


                    if(testEncryptCPABE): #CPABE ENCRYPTATION

                        if (testEncryptCPABE_CASE == 1):
                            #Decipher attribute value
                            codeValue, outValue = getstatusoutput(["java", "-jar", "./conf_files/jar/cpabe_decipher.jar",
                                                                str(body[key]["https://uri.etsi.org/ngsi-ld/hasValue"])])

                            if(codeValue == 0):
                                #Assign decipher attribute value
                                body[key]["https://uri.etsi.org/ngsi-ld/hasValue"] = outValue.decode('utf8')

                        if (testEncryptCPABE_CASE == 2):

                            #Decipher attribute value
                            codeValue, outValue = getstatusoutput(["java", "-jar", "./conf_files/jar/cpabe_decipher.jar",
                                                                str(body[key]["value"])])

                            if(codeValue == 0):
                                #Assign decipher attribute value
                                body[key]["value"] = outValue.decode('utf8')

            except Exception as e:
                print("Error procesing key: " + key)
                print(e)
                #return bodyBackUp, False

        return body, True

    except:
        return bodyBackUp, False

def pp_json(json_thing, sort=True, indents=4):
    if type(json_thing) is str:
        print(json.dumps(json.loads(json_thing), sort_keys=sort, indent=indents))

    else:
        print(json.dumps(json_thing, sort_keys=sort, indent=indents))
    return None


if __name__ == '__main__':

    gcontext = ssl.SSLContext()

    #Obtain configuracion from config.cfg file.
    cfg = configparser.ConfigParser()  
    cfg.read(["./config.cfg"])  
    
    keyrock_protocol = cfg.get("GENERAL", "keyrock_protocol")
    keyrock_host = cfg.get("GENERAL", "keyrock_host")
    keyrock_port = cfg.get("GENERAL", "keyrock_port")
    keyrock_user = cfg.get("GENERAL", "keyrock_user")
    keyrock_pass = cfg.get("GENERAL", "keyrock_pass")

    capman_protocol = cfg.get("GENERAL", "capman_protocol")
    capman_host = cfg.get("GENERAL", "capman_host")
    capman_port = cfg.get("GENERAL", "capman_port")

    policy_action = cfg.get("GENERAL", "policyGET_action")
    policy_device = cfg.get("GENERAL", "policyGET_device")
    policy_resource = cfg.get("GENERAL", "policyGET_resource")

    pep_protocol = cfg.get("GENERAL", "pep_protocol")
    pep_host = cfg.get("GENERAL", "pep_host")
    pep_port = cfg.get("GENERAL", "pep_port")

    headers = {"Content-Type":"application/json"}
    body = json.dumps({"name":keyrock_user,"password":keyrock_pass}).encode()

    keyRockMethod="POST"
    keyRockUri="/v1/auth/tokens"
    
    print("******* Sending authentication request to KeyRock... *******")
    print("Method: " + keyRockMethod)
    print("URI: " + keyRockUri)
    print("Headers: " + str(headers))
    print("Body: " + str(body))

    if(keyrock_protocol.upper()=="http".upper() or keyrock_protocol.upper()=="https".upper()):
        
        if(keyrock_protocol.upper()=="http".upper()):
            conn = http.client.HTTPConnection(keyrock_host,keyrock_port)
        else:
            #conn = http.client.HTTPSConnection(keyrock_host,keyrock_port,
            #                                    key_file="./certs/idm-2018-key.pem",
            #                                    cert_file="./certs/idm-2018-cert.pem",
            #                                    context=gcontext)

            conn = http.client.HTTPSConnection(keyrock_host,keyrock_port,
                                                context=gcontext)

        conn.request(keyRockMethod, keyRockUri, body, headers)
        response = conn.getresponse()

        status = response.status
        reason = response.reason
        data = response.read()
        conn.close()

        if(status==201):
            #Example format: keyRockToken = "4aece71b-8c22-4012-9397-608da3f58c6c"
            keyRockToken = response.headers["X-Subject-Token"]

            print("\nAUTH SUCCESS: Authentication Keyrock Token obtained : " + keyRockToken)

            headers = {"Content-Type":"application/json"}
            body = json.dumps({"token":keyRockToken,"ac":policy_action,"de":policy_device,"re":policy_resource}).encode()

            capmanMethod="POST"
            capmanUri="/"

            print("\n******* Sending authorisation request to Capability Manager... *******")
            print("Method: " + capmanMethod)
            print("URI: " + capmanUri)
            print("Headers: " + str(headers))
            print("Body: " + str(body))

            if(capman_protocol.upper()=="http".upper()):
                conn = http.client.HTTPConnection(capman_host,capman_port)
            else:
                #conn = http.client.HTTPSConnection(capman_host,capman_port,
                #                                key_file="./certs/idm-2018-key.pem",
                #                                cert_file="./certs/idm-2018-cert.pem",
                #                                context=gcontext)
                conn = http.client.HTTPSConnection(capman_host,capman_port,
                                                context=gcontext)

            conn.request(capmanMethod, capmanUri, body, headers)
            response = conn.getresponse()

            status = response.status
            reason = response.reason
            data = response.read()
            conn.close()

            if(status==200):

                bodyJSON = json.loads(data.decode('utf8').replace("'", '"'))
                print("\nSUCCESS: Authorisation Granted --> Capability token obtained : " + str(bodyJSON))


                headers = {"Accept":"application/ld+json",
                           "x-auth-token":json.dumps(bodyJSON)}

                print("\n******* Sending NGSI-LD query to MDR through PEP_PROXY... *******")
                print("Method: " + policy_action)
                print("URI: " + policy_resource)
                print("Headers: " + str(headers))

                if(pep_protocol.upper()=="http".upper()):
                    conn = http.client.HTTPConnection(pep_host,pep_port)
                else:
                    #conn = http.client.HTTPSConnection(pep_host,pep_port,
                    #                                key_file="./certs/idm-2018-key.pem",
                    #                                cert_file="./certs/idm-2018-cert.pem",
                    #                                context=gcontext)
                    conn = http.client.HTTPSConnection(pep_host,pep_port,
                                                    context=gcontext)
                conn.request(policy_action, policy_resource, None, headers)
                response = conn.getresponse()

                status = response.status
                reason = response.reason
                #data = response.read()
                headersPEPResponse = response.headers

                response.chunked = False
                respBody = ""
                while True:
                    chunk_size = get_chunk_size(response)
                    if (chunk_size == 0):
                        break
                    else:
                        chunk_data = get_chunk_data(response,chunk_size)
                        #print("Chunk Received: " + chunk_data.decode())
                        respBody += chunk_data.decode()

                conn.close()

                print("\nSUCCESS: NGSI-LD response:\n")
                print("* Code: " + str(status))
                print("* Message: " + str(reason))
                print("* Headers:\n" + str(headersPEPResponse))
                print("\n* Body(cpabe_cipher):\n" + json.dumps(json.loads(respBody), sort_keys=True, indent=4))

                decipherRespBody = json.loads(respBody)

                if (decipherRespBody.get("@id") or decipherRespBody.get("id")): 
                    decipherRespBody,statusDecipher = decipherBodyAttributes(decipherRespBody)

                #print(type(decipherRespBody))
                #print("* DecipherBody:")
                #print(json.loads(json.dumps(decipherRespBody)))
                #pp_json(decipherRespBody)

                print("\n* Body(cpabe_decipher):\n" + json.dumps(decipherRespBody, sort_keys=True, indent=4))

            else:
                print("\nFAILURE Authorisation Error --> Capability Manager.")
                print(data)
        else:
            print("\nFAILURE: Authentication Error --> Key Rock")
            print(json.loads(data.decode('utf8').replace("'", '"')))
    else:
        print("Incorrect value for 'keyrock_protocol': " + keyrock_protocol)

