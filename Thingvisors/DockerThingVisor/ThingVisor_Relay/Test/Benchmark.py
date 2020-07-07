import sys
import traceback
import paho.mqtt.client as mqtt
import time
import os
import socket
import json
from threading import Thread
import requests
from concurrent.futures import ThreadPoolExecutor, wait, as_completed, FIRST_COMPLETED

TOPIC_vTHING = "tenant1/ribbon-tv/vThingRibbon"

UNIT = 10**3

class mqttSilonThread(Thread):
    def __init__(self, MQTT_silo_broker_IP, MQTT_silo_broker_port):
        Thread.__init__(self)
        self.MQTT_silo_broker_IP = MQTT_silo_broker_IP
        self.MQTT_silo_broker_port = MQTT_silo_broker_port
        self.total_timestamp = 0

    def on_message_in_silo(self, mosq, obj, msg):
        arrived_timestamp = time.time() * (UNIT)
        payload = msg.payload.decode("utf-8", "ignore")

        jpayload = json.loads(payload)
        send_timestamp = jpayload["data"][0]["ribbon_time"]["value"]["timestamp"]
        msg_num = jpayload["data"][0]["ribbon_time"]["value"]["seq"]
        # print("on_message_in_silo ---> msg -->", msg.topic + " " + payload)
        delta_timestamp = arrived_timestamp - send_timestamp
        self.total_timestamp += delta_timestamp
        print("msg: %d, ∆ timestamp %.4f (ms), average: %.4f" % (msg_num, delta_timestamp, self.total_timestamp/msg_num))
        # print("NO DUMPS msg: %d, ∆ timestamp %.4f (ms), average: %.4f" % (msg_num, arrived_timestamp - timestamp_old, self.total_timestamp/msg_num))

    def run(self):
        print("Thread mqtt data started")
        global mqtt_silo_client
        mqtt_silo_client.connect(self.MQTT_silo_broker_IP, self.MQTT_silo_broker_port, 30)
        mqtt_silo_client.message_callback_add(TOPIC_vTHING, self.on_message_in_silo)
        mqtt_silo_client.subscribe(TOPIC_vTHING)
        mqtt_silo_client.loop_forever()
        print("Thread '" + self.name + "' terminated")



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


if __name__ == '__main__':

    MQTT_data_broker_IP = "127.0.0.1"
    MQTT_data_broker_port = 1883

    message = {
        "data": [
            {
                "id": "urn:ngsi-ld:vThingRibbon",
                "type": "time",
                "ribbon_time": {
                    "type": "Property",
                    "value": {
                        "seq": 1,
                        "timestamp": 313
                    }
                }
            }
        ],
        "meta": {
            "vThingID": "ribbon-tv/vThingRibbon"
        }
    }

    # timestamp_old = 0

    mqtt_ribbon_client = mqtt.Client()
    mqtt_silo_client = mqtt.Client()

    mqtt_ribbon_thread = mqttRibbonThread()
    mqtt_ribbon_thread.start()

    mqtt_silo_thread = mqttSilonThread(MQTT_silo_broker_IP="127.0.0.1", MQTT_silo_broker_port=32775)
    mqtt_silo_thread.start()

    # Test with ThreadPool
    pool = ThreadPoolExecutor(32)
    futures = []


    time.sleep(2)
    cnt = 1
    while True:
        try:

            time.sleep(1)
            message["data"][0]["ribbon_time"]["value"]["seq"] = cnt
            mqtt_ribbon_thread.send_message_in_ribbon(message)

            # Test with threadPool
            # futures.append(pool.submit(send_message_in_ribbon_test, cnt, message))

            # Test with POST
            # message["data"][0]["ribbon_time"]["value"]["timestamp"] = time.time()*(UNIT)
            # r = requests.post("http://172.17.0.10:8089/notify", data=json.dumps(message))

            cnt += 1
        except Exception as err:
            print("KeyboardInterrupt", err)
            time.sleep(1)
            os._exit(1)

