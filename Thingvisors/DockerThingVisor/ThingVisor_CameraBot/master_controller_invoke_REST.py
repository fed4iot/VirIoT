#!/usr/bin/python3
import argparse
import requests
import json
import os
from pathlib import Path


def login_as_admin_and_get_token(controllerurl,tenant_id,adminpassword):
    url = controllerurl+"/login"

    # tenant_id is == "admin"
    payload = {"userID": tenant_id, "password": adminpassword}
    print("  System vSilo logging as admin to mastercontroller url: " + controllerurl)
    #print("\n"+json.dumps(payload)+"\n")

    headers = {
        'accept': "application/json",
        'content-type': "application/json",
        'cache-control': "no-cache",
    }

    response = requests.request("POST", url, data=json.dumps(payload), headers=headers)

    if response.status_code in [201, 200]:
        token = response.json()["access_token"]
        return token
    else:
        print("    System vSilo could NOT login as admin to mastercontroller url: " + controllerurl)
        print("    " + response.text + "\n")
        # this empty return is crucial to signal a bad thing has occurred
        return ""

def printj(msg):
    print("\n")
    print(json.dumps(json.loads(msg), indent=4, sort_keys=True))
    print("\n")

def set_vthing_endpoint(controllerUrl,vThingID,endpoint,tenant_id,adminpassword):
    url = controllerUrl + "/setVThingEndpoint"
    print("Setting vThing endpoint, please wait ....")
    msg={}
    msg['vThingID'] = vThingID
    msg['endpoint'] = endpoint
    payload = json.dumps(msg)
    printj(payload)

    token = login_as_admin_and_get_token(controllerUrl,tenant_id,adminpassword)
    if not token:
        return
    headers = {
        'Authorization': "Bearer " + token,
        'accept': "application/json",
        'content-type': "application/json",
        'cache-control': "no-cache",
    }

    response = requests.request("POST", url, data=payload, headers=headers)
    print(response.json().get('message') + "\n")
