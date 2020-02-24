#!/usr/bin/python3
import argparse
import requests
import json
import os
from pathlib import Path

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


def init_args(parser):

    parser.set_defaults(func=run)
    parser.add_argument('-c', action='store', dest='controllerUrl',
                        help='Controller url (default: http://127.0.0.1:8090)', default='http://127.0.0.1:8090')


def run(args):
    url = args.controllerUrl+"/logout"
    token = get_token()
    if not token:
        return
    headers = {
        'Authorization': "Bearer " + token,
        'accept': "application/json",
        'content-type': "application/json",
        'cache-control': "no-cache"
        }

    response = requests.request("DELETE", url, headers=headers)
    print("\n"+response.text+"\n")
    os.remove(token_file)


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    init_args(parser)
    args = parser.parse_args()
    args.func(args)
