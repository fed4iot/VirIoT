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
    parser.add_argument('-r', action='store', dest='role',
                        help='role of the user: "user" or "admin" (default: user)', default='user')


def get_token():
    if not os.path.isfile(token_file):
        print("Token not found")
        return None
    with open(token_file, 'r') as file:
        data = json.load(file)
        token = data["access_token"]
        return token


def run(args):
    url = args.controllerUrl+"/register"
    token = get_token()
    if not token:
        return
    headers = {
        'Authorization': "Bearer " + token,
        'accept': "application/json",
        'content-type': "application/json",
        'cache-control': "no-cache"
        }
    payload = {"userID": args.userID, "password": args.password, "role": args.role}

    response = requests.request("POST", url, headers=headers, data=json.dumps(payload))
    print(response.json().get('message', response.text) + "\n")


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    init_args(parser)
    args = parser.parse_args()
    args.func(args)
