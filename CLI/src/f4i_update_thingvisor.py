#!/usr/bin/python3
import argparse
import json
import requests
import os
from pathlib import Path
from pprint import pprint

viriot_dir = str(Path.home())+"/.viriot"
token_file = viriot_dir+"/token"


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
    parser.add_argument('-p', action='store', dest='params',
                        help='ThingVisor params, JSON object (default: "") ', default='""')
    parser.add_argument('-d', action='store', dest='description',
                        help='ThingVisor description (default: \'hello thingVisor\')', default='hello thingVisor')
    parser.add_argument('-u', action='store', dest='updateInfo',
                        help='ThingVisor updateInfo: ephemeral information for the ThingVisor (default: "")', default='""')
    parser.set_defaults(func=run)


def run(args):
    url = args.controllerUrl+"/updateThingVisor"
    print("Updating Thing Visor, please wait ....")

    try:
        payload = {"thingVisorID": args.name,
                   "params": json.loads(args.params),
                   "description": args.description,
                   "updateInfo": json.loads(args.updateInfo),
                   }
    except ValueError as err:
        print("Error in JSON argument:", err)
        print("The syntax of the arguments \"-p\" and \"-u\" must be like: \'{\"key1\":\"value\", \"key2\":[\"value1\", \"value2\"]}\'")
        exit()
    except Exception as err:
        print("Error:", err)
        exit()


    pprint(payload)
    token = get_token()
    if not token:
        return
    headers = {
        'Authorization': "Bearer " + token,
        'accept': "application/json",
        'content-type': "application/json",
        'cache-control': "no-cache",
        }

    response = requests.request("POST", url, data=json.dumps(payload), headers=headers)
    print(response.json().get('message')+"\n")


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    init_args(parser)
    args = parser.parse_args()
    args.func(args)
