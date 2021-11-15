#!/usr/bin/env python

import time
import paho.mqtt.client as mqtt
import datetime
import sys

host = "localhost"
port = 1883
keepalive = 60
Pana_topic = "Pana/"

FACE_PANA ='FACE_PANA'
MOVE_PANA ='MOVE_PANA'

if __name__ == '__main__':

    args = sys.argv

    if args[1] == "pana_cam":
        topic = Pana_topic + args[1]
        print(topic)

    else:
        print("error: pana_cam")
        exit()

    if args[2] == "fp":
        msg =FACE_PANA

    elif args[2] == "mp":
        msg =MOVE_PANA
	
    else:
        print("error:  fp or mp")
        exit()

    client = mqtt.Client()
    client.connect(host, port, keepalive)

    for i in range(1):
            client.publish(topic, msg)
            time.sleep(2)

    client.disconnect()
