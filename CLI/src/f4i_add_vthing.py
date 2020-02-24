#!/usr/bin/python3
import argparse
import requests
import json
import os
from pathlib import Path

viriot_dir = str(Path.home()) + "/.viriot"
token_file = viriot_dir + "/token"


def get_token():
    if not os.path.isfile(token_file):
        print("Token not found")
        return None
    with open(token_file, 'r') as file:
        data = json.load(file)
        token = data["access_token"]
        return token


def printj(msg):
    print("\n")
    print(json.dumps(json.loads(msg), indent=4, sort_keys=True))
    print("\n")


def init_args(parser):
    parser.add_argument('-c', action='store', dest='controllerUrl',
                        help='Controller url (default: http://127.0.0.1:8090)', default='http://127.0.0.1:8090')
    parser.add_argument('-t', action='store', dest='tenantID',
                        help='tenantID (default: tenant1)', default='tenant1')
    parser.add_argument('-s', action='store', dest='vSiloName',
                        help='Name of the vSilo used to distinguish the different vSilos of the same tenant (default: Silo1, unique per tenant). The unique identifier (vSiloID) of the vSilo in the system is <tenantID>_<vSiloName>',
                        default='Silo1')
    parser.add_argument('-v', action='store', dest='vThingID',
                        help='vThingID (default: helloWorld/hello)', default='helloWorld/hello')
    parser.set_defaults(func=run)


def run(args):
    url = args.controllerUrl + "/addVThing"
    print("Adding IoT vThing, please wait ....")

    payload = "{\n\t\"tenantID\":\"" + args.tenantID + "\",\n" \
                                                       "\t\"vThingID\":\"" + args.vThingID + "\",\n" \
                                                                                             "\t\"vSiloName\":\"" + args.vSiloName + "\"}"
    printj(payload)

    token = get_token()
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


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    init_args(parser)
    args = parser.parse_args()
    args.func(args)
