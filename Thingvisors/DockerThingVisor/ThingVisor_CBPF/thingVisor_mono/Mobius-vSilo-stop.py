#! /usr/bin/python3 

import requests
import json

vSiloBrokerIP = "192.168.11.101"
#vSiloBrokerIP = "192.168.100.18"
#vSiloBrokerIP = "localhost"
#port = "32600"
#port = "32780"
port = "31598"

url_prefix = "http://"+vSiloBrokerIP+":" + port +"/Mobius/cbpf:detector/cbpf:detector/"

headers = {
        'accept': "application/json",
        'x-m2m-ri': "12345",
        'x-m2m-origin': 'S',
        'content-type': "application/vnd.onem2m-res+json;ty=4",
        'cache-control': "no-cache",
}

command = "stop"
url = url_prefix+command
con = {"cmd-value": {"job": "dsfds"}, "cmd-qos":2}
payload = {"m2m:cin": {"con": con}}
response = requests.request("POST", url, headers=headers, data = json.dumps(payload))
print(response.text.encode('utf8'))
