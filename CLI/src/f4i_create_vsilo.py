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
    url = args.controllerUrl + "/siloCreate"
    print("Creating IoT silo, please wait ....")

    payload = "{\n\t\"tenantID\":\"" + args.tenantID + \
              "\",\n\t\"vSiloName\":\"" + args.vSiloName + \
              "\",\n\t\"flavourID\":\"" + args.flavourName + \
              "\",\n\t\"vSiloZone\":\"" + args.vSiloZone + \
              "\",\"debug_mode\":" + args.debug_mode + "\n}"
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
    parser.add_argument('-s', action='store', dest='vSiloName',
                        help='Name of the vSilo used to distinguish the different vSilos of the same tenant (default: Silo1, unique per tenant). The unique identifier (vSiloID) of the vSilo in the system is <tenantID>_<vSiloName>',
                        default='Silo1')
    parser.add_argument('-t', action='store', dest='tenantID',
                        help='tenantID (default: tenant1)', default='tenant1')
    parser.add_argument('-f', action='store', dest='flavourName',
                        help='flavourID of the IoT silo(default: Mobius-base-f)', default='Mobius-base-f')
    parser.add_argument('-z', action='store', dest='vSiloZone',
                        help='Zone in which the vsilo will be deployed', default='')
    parser.add_argument('-d', action='store', dest='debug_mode',
                        help='debug mode only storing info in the systemDB, boolean (default: false)', default="false")
    parser.set_defaults(func=run)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    init_args(parser)
    args = parser.parse_args()
    args.func(args)
