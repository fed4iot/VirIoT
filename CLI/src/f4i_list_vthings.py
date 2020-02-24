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


def init_args(parser):
    parser.set_defaults(func=run)
    parser.add_argument('-c', action='store', dest='controllerUrl',
                        help='Controller url (default: http://127.0.0.1:8090)', default='http://127.0.0.1:8090')


def run(args):
    url = args.controllerUrl + "/listVThings"
    token = get_token()
    if not token:
        return
    headers = {
        'Authorization': "Bearer " + token,
        'accept': "application/json",
        'content-type': "application/json",
        'cache-control': "no-cache",
    }

    response = requests.request("GET", url, headers=headers)
    if response.status_code in [201, 200]:
        printj(response.text)
    else:
        print(response.json().get('message', response.text) + "\n")


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    init_args(parser)
    args = parser.parse_args()
    args.func(args)
