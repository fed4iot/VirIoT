#! /usr/bin/python3 

import sys
import base64
import requests
import json
import time

#vSiloBrokerIP = "192.168.100.18"
#vSiloBrokerIP = "localhost"
#port = "32780"
vSiloBrokerIP = "192.168.11.101"
port = "31598"

url_prefix = "http://"+vSiloBrokerIP+":" + port +"/Mobius/cbpf-mono:detector/cbpf-mono:detector/"

headers = {
        'accept': "application/json",
        'x-m2m-ri': "12345",
        'x-m2m-origin': 'S',
        'content-type': "application/vnd.onem2m-res+json;ty=4",
        'cache-control': "no-cache",
}

def encode_base64url(s):
    return base64.urlsafe_b64encode(s).rstrip(b'=')

def decode_base64url(s):
    return base64.urlsafe_b64decode(s + b'=' * ((4 - len(s) & 3) & 3))

file = sys.argv[1]
with open(file, 'rb') as f:
    img = f.read()
img_msg = encode_base64url(img).decode('utf-8')

command = "start"
url = url_prefix+command
con = {"cmd-value": {"job": "dsfds", "img": img_msg }, "cmd-qos":2}
payload = {"m2m:cin": {"con": con}}
response = requests.request("POST", url, headers=headers, data = json.dumps(payload))
print(response.text.encode('utf8'))
