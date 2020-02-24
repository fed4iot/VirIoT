#!/usr/bin/python3
import argparse
import json
import requests
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
    parser.add_argument('-n', action='store', dest='name',
                        help='ThingVisor ID (default: helloWorld)', default='helloWorld')
    parser.add_argument('-f', action='store_true', dest='force', help='Force ThingVisor deletion (default: false)')
    parser.set_defaults(func=run)


def run(args):
    url = args.controllerUrl + "/deleteThingVisor"
    print("Deleting ThingVisor, please wait ....")

    # payload = "{\n\t\"thingVisorID\":\"" + args.name + "\", \"force\":" + args.force + "\n}"
    payload_json = {"thingVisorID": args.name,
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


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    init_args(parser)
    args = parser.parse_args()
    args.func(args)
