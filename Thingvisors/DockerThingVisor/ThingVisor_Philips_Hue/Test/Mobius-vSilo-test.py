#! /usr/bin/python3 

import requests
import json
import time

vSiloBrokerIP = "172.17.0.5"
port = "7579"

url_prefix = "http://"+vSiloBrokerIP+":" + port +"/Mobius/phueactuator:light1/phueactuator:light1/"

headers = {
        'accept': "application/json",
        'x-m2m-ri': "12345",
        'x-m2m-origin': 'S',
        'content-type': "application/vnd.onem2m-res+json;ty=4",
        'cache-control': "no-cache",
}

# switch on light 1
for i in range(2):
    command = "set-on"
    url = url_prefix+command
    con = {"cmd-value": False, "cmd-qos":0}
    payload = {"m2m:cin": {"con": con}}
    response = requests.request("POST", url, headers=headers, data = json.dumps(payload))
    print(response.text.encode('utf8'))
    time.sleep(2)  
    con = {"cmd-value": True, "cmd-qos":0}
    payload = {"m2m:cin": {"con": con}}
    response = requests.request("POST", url, headers=headers, data = json.dumps(payload))
    print(response.text.encode('utf8'))
    time.sleep(2)  

# cicle on hue
command = "set-hue"
url = url_prefix+command
print(url)
for hue in range(1,65535,5000):
    con = {"cmd-value": hue, "cmd-qos":0}   # QoS 0 means no feedback from the actuator
    payload = {"m2m:cin": {"con": con}}
    response = requests.request("POST", url, headers=headers, data = json.dumps(payload))
    print(response.text.encode('utf8'))
    time.sleep(0.5)  

time.sleep(1) 
# switch off light 2
for i in range(1):
    command = "set-on"
    url = url_prefix+command
    con = {"cmd-value": False, "cmd-qos":0}
    payload = {"m2m:cin": {"con": con}}
    response = requests.request("POST", url, headers=headers, data = json.dumps(payload))
    print(response.text.encode('utf8'))
    time.sleep(1)  
