#! /usr/bin/python3 

import requests
import json
import time

url_prefix = "http://172.17.0.4:7579/Mobius/pHueActuator:light1/pHueActuator:light1/"

headers = {
        'accept': "application/json",
        'x-m2m-ri': "12345",
        'x-m2m-origin': 'S',
        'content-type': "application/vnd.onem2m-res+json;ty=4",
        'cache-control': "no-cache",
}

# switch on light 1
for i in range(10):
    command = "set-on"
    url = url_prefix+command
    con = {"cmd-value": False, "cmd-qos":0}
    payload = {"m2m:cin": {"con": con}}
    response = requests.request("POST", url, headers=headers, data = json.dumps(payload))
    print(response.text.encode('utf8'))
    time.sleep(0.2)  
    con = {"cmd-value": True, "cmd-qos":0}
    payload = {"m2m:cin": {"con": con}}
    response = requests.request("POST", url, headers=headers, data = json.dumps(payload))
    print(response.text.encode('utf8'))
    time.sleep(0.2)  

# cicle on hue
command = "set-hue"
url = url_prefix+command
print(url)
for hue in range(1,65535,1000):
    con = {"cmd-value": hue, "cmd-qos":0}   # QoS 0 means no feedback from the actuator
    payload = {"m2m:cin": {"con": con}}
    response = requests.request("POST", url, headers=headers, data = json.dumps(payload))
    time.sleep(0.2)  
    print(response.text.encode('utf8'))
