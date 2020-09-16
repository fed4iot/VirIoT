#!/usr/bin/python3
import argparse
import json
import requests
import os
from pathlib import Path
import yaml
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


def get_yaml_file(yaml_path):
    yaml_list = []
    if yaml_path is not "":
        with open(yaml_path) as f:
            yamls = yaml.safe_load_all(f)
            print(type(yamls))
            for item in yamls:
                yaml_list.append(item)
                # pprint(a)
            return yaml_list


def init_args(parser):
    parser.add_argument('-c', action='store', dest='controllerUrl',
                        help='Controller url (default: http://127.0.0.1:8090)', default='http://127.0.0.1:8090')
    parser.add_argument('-i', action='store', dest='imageName',
                        help='image name (default: "")', default='')
    parser.add_argument('-n', action='store', dest='name',
                        help='ThingVisor ID (default: helloworld-tv)', default='helloworld-tv')
    parser.add_argument('-p', action='store', dest='params',
                        help='ThingVisor params, JSON object (default: '') ', default='')
    parser.add_argument('-d', action='store', dest='description',
                        help='ThingVisor description (default: hello thingVisor)', default='hello thingVisor')
    parser.add_argument('-y', action='store', dest='yamlFilesPath',
                        help='yamlFilesPath (default: no yaml files)',
                        default='')
    parser.add_argument('-z', action='store', dest='tvZone',
                        help='Zone in which the ThingVisor will be deployed', default='')
    parser.add_argument('--debug', action='store_true', dest='debug_mode',
                        help='debug mode, boolean (default: false)', default="false")
    parser.set_defaults(func=run)


def run(args):
    url = args.controllerUrl+"/addThingVisor"
    print("Adding Thing Visor, please wait ....")

    yaml_list = get_yaml_file(args.yamlFilesPath)

    payload = {"imageName": args.imageName,
               "thingVisorID": args.name,
               "params": args.params,
               "description": args.description,
               "debug_mode": False if args.debug_mode == "false" else True,
               "tvZone": args.tvZone,
               "yamlFiles": yaml_list}

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
