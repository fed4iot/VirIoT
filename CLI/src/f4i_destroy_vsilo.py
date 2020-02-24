#!/usr/bin/python3
import argparse
import json
import os
import requests
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


def run(args):
    url = args.controllerUrl + "/siloDestroy"

    print("Removing IoT silo, please wait ....")
    # payload = "{\n\t\"tenantID\":\"" + args.tenantID + "\",\n\t\"vSiloName\":\"" + args.vSiloName + "\",\"force\":" + args.force + "\"\n}"
    payload_json = {"tenantID": args.tenantID,
                    "vSiloName": args.vSiloName,
                    "force": args.force}
    payload = json.dumps(payload_json)
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


def init_args(parser):
    # insert here the parser argument. This function is used by parent f4i.py

    parser.add_argument('-c', action='store', dest='controllerUrl',
                        help='Controller url (default: http://127.0.0.1:8090)', default='http://127.0.0.1:8090')
    parser.add_argument('-t', action='store', dest='tenantID',
                        help='tenantID (default: tenant1)', default='tenant1')
    parser.add_argument('-s', action='store', dest='vSiloName',
                        help='vSiloName (default: Silo1)', default='Silo1')
    parser.add_argument('-f', action='store_true', dest='force', help='Force Silo destruction (default: False)',
                        default=False)
    parser.set_defaults(func=run)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    init_args(parser)
    args = parser.parse_args()
    args.func(args)
