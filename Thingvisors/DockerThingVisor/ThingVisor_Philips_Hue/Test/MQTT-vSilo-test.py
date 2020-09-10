#! /usr/bin/python3 

import paho.mqtt.client as mqtt
import json
import time

vSiloBrokerIP = "172.17.0.4"
vSiloBrokerPort = 1883
client_mqtt = mqtt.Client()
client_mqtt.connect(vSiloBrokerIP, vSiloBrokerPort, 10)
entity_id = "phueactuator:light1"
vThingID = "phueactuator/light1"
tenantID = "tenant1"
topic_prefix = tenantID+"/"+vThingID+"/"+entity_id+"/"

# switch on light 1
command = "set-on"
topic = topic_prefix + command
print(topic)    
for i in range(2):
    con = {"cmd-value": False, "cmd-qos":0}
    client_mqtt.publish(topic,json.dumps(con),qos=0)
    time.sleep(2)  
    con = {"cmd-value": True, "cmd-qos":0}
    client_mqtt.publish(topic,json.dumps(con),qos=0)
    time.sleep(2)  

# cicle on hue
command = "set-hue"
topic = topic_prefix + command
print(topic)
for hue in range(1,65535,5000):
    con = {"cmd-value": hue, "cmd-qos":0}   # QoS 0 means no feedback from the actuator
    client_mqtt.publish(topic,json.dumps(con),qos=0)
    time.sleep(0.5)  

time.sleep(1) 
# switch off light 1
command = "set-on"
topic = topic_prefix + command  
print(topic)
for i in range(1):
    command = "set-on"
    con = {"cmd-value": False, "cmd-qos":0}
    client_mqtt.publish(topic,json.dumps(con),qos=0)
    time.sleep(2)  
