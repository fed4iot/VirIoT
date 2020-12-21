import argparse, argcomplete
import sys
import traceback
import paho.mqtt.client as mqtt
import time
import os
import socket
import json
from threading import Thread
import requests
import random
import string

UNIT = 10**3

def random_char(y):
       return ''.join(random.choice(string.ascii_letters) for x in range(y))

class mqttSilonThread(Thread):
    def __init__(self, MQTT_silo_broker_IP, MQTT_silo_broker_port):
        Thread.__init__(self)
        self.MQTT_silo_broker_IP = MQTT_silo_broker_IP
        self.MQTT_silo_broker_port = MQTT_silo_broker_port
        self.total_timestamp = 0
        self.samples = 0

    def run(self):
        print("Thread mqtt PRODUCER started")
        global mqtt_silo_client
        mqtt_silo_client.connect(self.MQTT_silo_broker_IP, self.MQTT_silo_broker_port, 30)
        mqtt_silo_client.loop_forever()
        print("Thread '" + self.name + "' terminated")

if __name__ == '__main__':

    try:
        parser = argparse.ArgumentParser()
        parser.add_argument('-t', action='store', dest='tenantID',
                            help='tenantID (default: tenant1)', default='tenant1')
        parser.add_argument('-b', action='store', dest='serverIP', 
                            help='MQTT vSilo Server Address (default: 127.0.0.1) ', default='127.0.0.1')
        parser.add_argument('-p', action='store', dest='serverPort', 
                            help='MQTT vSilo Server Port (default: 32776) ', default='32776')
        parser.add_argument('-i', action='store', dest='vThingID', 
                            help='vThingID (default: relay-tv/timestamp) ', default='relay-tv/timestamp')
        parser.add_argument('-r', action='store', dest='rate', 
                            help='Message rate msg/s (default: 1 msg/s)', default='1')
        parser.add_argument('-s', action='store', dest='payloadsize', 
                            help='Payloadsize in characters (default: 10 chars)', default='10')
        parser.add_argument('-v', action='store_true', dest='verbose', 
                            help='Print verbose output')
                            
        argcomplete.autocomplete(parser)
        args = parser.parse_args()
    except Exception:
        traceback.print_exc()

    MQTT_silo_broker_IP = args.serverIP
    MQTT_silo_broker_port=int(args.serverPort)
    tenantID = args.tenantID
    TOPIC_vTHING = tenantID+"/"+args.vThingID+"/testMQTTmessage"

    mqtt_silo_client = mqtt.Client()
    mqtt_silo_thread = mqttSilonThread(MQTT_silo_broker_IP, MQTT_silo_broker_port)
    mqtt_silo_thread.start()


    time.sleep(2)
    value = {
        "timestamp": 313,
        "sqn":0
    }
    msg = {
        "value": value
    }
    message = {
        "msg": msg
    }
    cnt = 1
    while True:
        try:
            time.sleep(1.0/float(args.rate))
            message['msg']['value']['timestamp'] = int(round(time.time()*(UNIT)))
            message['msg']['value']['sqn'] = cnt
            message['msg']['value']['payloadstring'] = random_char(int(args.payloadsize))
            data = json.dumps(message)
            mqtt_silo_client.publish(TOPIC_vTHING, payload=data)
            cnt += 1
            if args.verbose:
                print("Message sent: "+data)
        except Exception as err:
            print("KeyboardInterrupt", err)
            time.sleep(1)
            os._exit(1)

