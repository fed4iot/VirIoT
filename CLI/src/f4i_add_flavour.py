#!/usr/bin/python3
import argparse
import json
import requests
import os
from pathlib import Path
import yaml
from pprint import pprint

CRED = '\033[31m'
CEND = '\033[0m'
viriot_dir = str(Path.home())+"/.viriot"
token_file = viriot_dir+"/token"

def printj(msg):
    print("\n")
    print(json.dumps(json.loads(msg), indent=4, sort_keys=True))
    print("\n")


def get_token():
    if not os.path.isfile(token_file):
        print("Token not found")
        return None
    with open(token_file, 'r') as file:
        data = json.load(file)
        token = data["access_token"]
        return token

def get_yaml_file(yaml_path):
    yaml_list = []
    if yaml_path is not "":
        with open(yaml_path) as f:
            yamls = yaml.safe_load_all(f)
            for element in yamls:
                yaml_list.append(element)
                # pprint(a)
            return yaml_list

def run(args):
    url = args.controllerUrl + "/addFlavour"
    print("Adding Flavour, please wait ....\n")

    yaml_list = get_yaml_file(args.yamlFilesPath)

    # yaml_list = []
    # if args.yamlFilesPath is not "":
    #     with open(args.yamlFilesPath) as f:
    #         yamls = yaml.safe_load_all(f)
    #         print(type(yamls))
    #         for a in yamls:
    #             yaml_list.append(a)
    #             pprint(a)

    try:
        payload = {"imageName": args.imageName,
                   "thingVisorID": args.name,
                   "params": json.loads(args.params),
                   "description": args.description,
                   "debug_mode": False if args.debug_mode == "false" else True,
                   "tvZone": args.tvZone,
                   "yamlFiles": yaml_list}
    except Exception as err:
        print("Error adding ThingVisor:", err)
        print("The syntax of the arguments \"-s\" must be like: \'{\"key1\":\"value\", \"key2\":[\"value1\", \"value2\"]}\'")
        exit()
    # payload = "{\n\t\"flavourID\":\"" + args.flavourID + "\",\n\t\"flavourParams\":\"" + args.flavourParams + "\",\n\t\"imageName\":\"" + args.imageName + "\",\n\t\"flavourDescription\":\"" + args.description + "\"\n,\n\t\"yamlFile\":" + json.dumps(j_yaml) + "\n}"

    try:
        print(args.flavourParams)
        print(type(json.loads(args.flavourParams)))
        payload = {"flavourID": args.flavourID,
                   "flavourParams": json.loads(args.flavourParams),
                   "imageName": args.imageName,
                   "flavourDescription": args.description,
                   "yamlFiles": yaml_list}
        # printj(payload)
    except Exception as err:
        print("Error adding ThingVisor:", err)
        exit()

    print(payload)

    token = get_token()
    if not token:
        return
    headers = {
        'Authorization': "Bearer " + token,
        'accept': "application/json",
        'content-type': "application/json",
        'cache-control': "no-cache",
    }

    try:
        response = requests.request("POST", url, data=json.dumps(payload), headers=headers)
        print(json.loads(response.text)['message'] + "\n")
        print("Status can be controlled also with 'f4i.py list-flavours' CLI command")

    except Exception as err:
        print("Error adding Flavour:", err)
        exit()

def init_args(parser):
    # insert here the parser argument. This function is used by parent f4i.py
    parser.add_argument('-c', action='store', dest='controllerUrl',
                        help='Controller url (default: http://127.0.0.1:8090)', default='http://127.0.0.1:8090')
    parser.add_argument('-f', action='store', dest='flavourID',
                        help='flavourID (default: Mobius-base-f)', default='Mobius-base-f')
    parser.add_argument('-s', action='store', dest='flavourParams',
                        help='flavourParams (default: Mobius)', default='"Mobius"')
    parser.add_argument('-i', action='store', dest='imageName',
                        help='image name (default: '')', default='')
    parser.add_argument('-d', action='store', dest='description',
                        help='description (default: silo flavour formed by a oneM2M Mobius broker)',
                        default='Silo flavour formed by a oneM2M Mobius broker')
    parser.add_argument('-y', action='store', dest='yamlFilesPath',
                        help='yamlFilesPath (default: no yaml files)',
                        default='')
    parser.set_defaults(func=run)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    init_args(parser)
    args = parser.parse_args()
    args.func(args)