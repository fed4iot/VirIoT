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

UNIT = 10**3

class mqttSilonThread(Thread):
    def __init__(self, MQTT_silo_broker_IP, MQTT_silo_broker_port):
        Thread.__init__(self)
        self.MQTT_silo_broker_IP = MQTT_silo_broker_IP
        self.MQTT_silo_broker_port = MQTT_silo_broker_port
        self.total_timestamp = 0
        self.samples = 0

    def on_message_in_silo(self, mosq, obj, msg):
        global csvFile
        received_timestamp = int(round(time.time() * (UNIT)))
        payload = msg.payload.decode("utf-8", "ignore")

        try:
            jpayload = json.loads(payload)    
            send_timestamp = jpayload["msg"]["value"]["timestamp"]
            msg_num = jpayload["msg"]["value"]["sqn"]
            self.samples = self.samples+1
            #print("on_message_in_silo ---> msg -->", msg.topic + " " + payload)
            delta_timestamp = received_timestamp - send_timestamp
            self.total_timestamp += delta_timestamp
            print("msg: %d, delta timestamp %.4f (ms), average: %.4f" % (msg_num, delta_timestamp, self.total_timestamp/self.samples))
            if csvFile is not None:
                csvFile.write("%d \t %.4f \t %.4f \n" % (msg_num, delta_timestamp, self.total_timestamp/self.samples))
                csvFile.flush()
            # print("NO DUMPS msg: %d, ∆ timestamp %.4f (ms), average: %.4f" % (msg_num, arrived_timestamp - timestamp_old, self.total_timestamp/msg_num))
        except Exception as err:
            print("Bad notification format", err)
            return 'Bad notification format', 401

    def run(self):
        print("Thread mqtt data started")
        global mqtt_silo_client
        mqtt_silo_client.connect(self.MQTT_silo_broker_IP, self.MQTT_silo_broker_port, 30)
        mqtt_silo_client.message_callback_add(TOPIC_vTHING, self.on_message_in_silo)
        mqtt_silo_client.subscribe(TOPIC_vTHING)
        mqtt_silo_client.loop_forever()
        print("Thread '" + self.name + "' terminated")

if __name__ == '__main__':

    try:
        parser = argparse.ArgumentParser()
        parser.add_argument('-t', action='store', dest='tenantID',
                            help='tenantID (default: tenant1)', default='tenant1')
        parser.add_argument('-s', action='store', dest='serverIP', 
                            help='MQTT vSilo Server Address (default: 127.0.0.1) ', default='127.0.0.1')
        parser.add_argument('-p', action='store', dest='serverPort', 
                            help='MQTT vSilo Server Port (default: 32776) ', default='32776')
        parser.add_argument('-v', action='store', dest='vThingID', 
                            help='vThingID (default: relay-tv/timestamp) ', default='relay-tv/timestamp')
        parser.add_argument('-f', action='store', dest='csvFileName', 
                            help='csvFile (default: None) ', default=None)
                            
        argcomplete.autocomplete(parser)
        args = parser.parse_args()
    except Exception:
        traceback.print_exc()

    MQTT_silo_broker_IP = args.serverIP
    MQTT_silo_broker_port=int(args.serverPort)
    tenantID = args.tenantID
    TOPIC_vTHING = tenantID+"/"+args.vThingID+"/#"
    
    csvFileName = args.csvFileName
    csvFile = None
    if csvFileName is not None:
        csvFile =  open(csvFileName, "w")

    mqtt_silo_client = mqtt.Client()
    mqtt_silo_thread = mqttSilonThread(MQTT_silo_broker_IP, MQTT_silo_broker_port)
    mqtt_silo_thread.start()


    time.sleep(2)
    while True:
        try:
            time.sleep(1)
        except Exception as err:
            print("KeyboardInterrupt", err)
            if csvFile is not None:
                csvFile.close()
            time.sleep(1)
            os._exit(1)

