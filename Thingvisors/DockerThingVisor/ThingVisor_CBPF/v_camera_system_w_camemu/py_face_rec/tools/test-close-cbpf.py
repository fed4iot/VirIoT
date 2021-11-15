#! /usr/bin/python3 
import kafka
import requests
import json
import base64
import time

from logging import basicConfig, getLogger, INFO

basicConfig(level=INFO)
logger = getLogger(__name__)

testImgName = "test.jpg"

CONTROL_BROKER = "133.9.250.209:9092"
CONTROL_TOPIC = "control_in"
TIMEOUT = 10000

with open(testImgName, 'rb') as f:
    srcImg = f.read()

binImg = base64.b64encode(srcImg).decode('utf-8')

params = {"content": {"value": binImg},
          "file name": {"value": testImgName}}

payload = {
    "cmd-value":"close",
    "cmd-qos":"2",
    #"cmd-params": params
    }
payload = json.dumps(payload)

#print (payload)

control_broker = kafka.KafkaProducer(bootstrap_servers=CONTROL_BROKER,
    max_request_size=15728640,api_version_auto_timeout_ms=int(TIMEOUT))

#message = "hello"

#control_broker.send(CONTROL_TOPIC, message.encode('utf-8'))
control_broker.send(CONTROL_TOPIC, payload.encode('utf-8'))
time.sleep(1)

#print (control_broker.metrics())

print ("publish")
