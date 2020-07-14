import argparse, argcomplete
import sys
import traceback
import time
import os
import socket
import json
from threading import Thread
import requests

#TOPIC_vTHING = "tenant1/ribbon-tv/vThingRibbon"

UNIT = 10**3

'''
class mqttRibbonThread(Thread):
    def __init__(self):
        Thread.__init__(self)

    def send_message_in_ribbon(self, payload):
        # global timestamp_old

        payload["data"][0]["ribbon_time"]["value"]["timestamp"] = time.time() * (UNIT)
        mqtt_ribbon_client.publish("ribbonTopic", payload=json.dumps(payload))
        # jpayload = json.dumps(payload)
        # timestamp_old = time.time() * (UNIT)
        # mqtt_ribbon_client.publish("ribbonTopic", payload=jpayload)

    def run(self):
        print("Thread mqtt ribbon started")
        global mqtt_ribbon_client
        mqtt_ribbon_client.connect(MQTT_data_broker_IP, MQTT_data_broker_port, 30)
        mqtt_ribbon_client.loop_forever()
        print("Thread '" + self.name + "' terminated")


def send_message_in_ribbon_test(seq, payload):
    message["data"][0]["ribbon_time"]["value"]["seq"] = seq
    payload["data"][0]["ribbon_time"]["value"]["timestamp"] = time.time() * (UNIT)
    mqtt_ribbon_client.publish("ribbonTopic", payload=json.dumps(payload))

'''
if __name__ == '__main__':

    #MQTT_data_broker_IP = "127.0.0.1"
    #MQTT_data_broker_port = 1883

    message = {
        "timestamp": 313,
        "sqn":0
    }

    # timestamp_old = 0

    #mqtt_ribbon_client = mqtt.Client()
    #mqtt_silo_client = mqtt.Client()

    #mqtt_ribbon_thread = mqttRibbonThread()
    #mqtt_ribbon_thread.start()

    #mqtt_silo_thread = mqttSilonThread(MQTT_silo_broker_IP="127.0.0.1", MQTT_silo_broker_port=32775)
    #mqtt_silo_thread.start()

    # Test with ThreadPool
    #pool = ThreadPoolExecutor(32)
    #futures = []

    try:
        parser = argparse.ArgumentParser()
        parser.add_argument('-t', action='store', dest='thingVisorUrl',
                            help='ThingVisorUrl (default: http://172.17.0.3:8089/notify)', default='http://172.17.0.3:8089/notify')
        parser.add_argument('-r', action='store', dest='rate', 
                            help='Message rate msg/s (default: 1 msg/s)', default='1')
        argcomplete.autocomplete(parser)
        args = parser.parse_args()
    except Exception:
        traceback.print_exc()

    time.sleep(2)
    cnt = 1
    while True:
        try:
            time.sleep(1.0/float(args.rate))
            #message["data"][0]["ribbon_time"]["value"]["seq"] = cnt
            #mqtt_ribbon_thread.send_message_in_ribbon(message)

            # Test with threadPool
            # futures.append(pool.submit(send_message_in_ribbon_test, cnt, message))

            # Test with POST
            message['timestamp'] = int(round(time.time()*(UNIT)))
            message['sqn'] = cnt
            data = json.dumps(message)
            r = requests.post(args.thingVisorUrl, json=data)
            cnt += 1
            print("Message sent: "+data)
        except Exception as err:
            print("KeyboardInterrupt", err)
            time.sleep(1)
            os._exit(1)

