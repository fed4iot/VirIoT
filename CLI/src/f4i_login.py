#!/usr/bin/python3
import argparse
import requests
import json
import os
from pathlib import Path


viriot_dir = str(Path.home())+"/.viriot"
token_file = viriot_dir+"/token"

def init_args(parser):

    parser.set_defaults(func=run)
    parser.add_argument('-c', action='store', dest='controllerUrl',
                        help='Controller url (default: http://127.0.0.1:8090)', default='http://127.0.0.1:8090')
    parser.add_argument('-u', action='store', dest='userID',
                        help='user identifier (default: tenant1)', default='tenant1')
    parser.add_argument('-p', action='store', dest='password',
                        help='password (default: password)', default='password')


def run(args):
    url = args.controllerUrl+"/login"

    payload = {"userID": args.userID, "password": args.password}
    print("\n"+json.dumps(payload)+"\n")

    headers = {
        'accept': "application/json",
        'content-type': "application/json",
        'cache-control': "no-cache",
        }

    response = requests.request("POST", url, data=json.dumps(payload), headers=headers)

    if response.status_code in [201, 200]:
        print(json.dumps(response.json()))
        if not os.path.exists(viriot_dir):
            os.makedirs(viriot_dir)
        with open(token_file, 'w') as file:
            file.write(json.dumps({"access_token": response.json()["access_token"]}))
    else:
        print(response.text+"\n")


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    init_args(parser)
    args = parser.parse_args()
    args.func(args)
