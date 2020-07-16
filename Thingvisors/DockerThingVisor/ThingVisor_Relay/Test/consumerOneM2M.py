import argparse
import argcomplete
import sys
import traceback
import paho.mqtt.client as mqtt
import time
import os
import socket
import urllib
import json
from threading import Thread
from flask import Flask
from flask import json
from flask import request
import signal
import F4Im2m

UNIT = 10**3

app = Flask(__name__)
flask_port = 5000

class oneM2MMQTTSiloThread(Thread):
    def __init__(self):
        Thread.__init__(self)


    def run(self):
        global total_timestamp, samples, mqtt_silo_client
        print("Thread oneM2M data started")
        print("Mobius subscription" + " " + origin + " " + str(notification_URI) + " " + cnt_arn + " " + CSE_url)
        # notification topic actually is /oneM2M/req/Mobius/notify/json
        topic = "/oneM2M/req/Mobius/notify/json"
        nuri = ["mqtt://127.0.0.1/notify"]
        status, sub = F4Im2m.sub_create(sub_rn, origin, nuri, "Mobius/" + cnt_arn, CSE_url)
        total_timestamp = 0
        samples = 0
        if status == 404:
            print(sub)
            sys.exit()
        time.sleep(0.05)

        mqtt_silo_client = mqtt.Client()
        mqtt_silo_client.connect(urllib.parse.urlparse(CSE_url).hostname, 1883, 30)
        mqtt_silo_client.message_callback_add(topic, self.on_receive_MQTT)
        mqtt_silo_client.subscribe(topic)
        mqtt_silo_client.loop_forever()
        print("Thread '" + self.name + "' terminated")

    def on_receive_MQTT(self,mosq, obj, msg):
        payload = msg.payload.decode("utf-8", "ignore")
        try:
            jres = json.loads(payload)
            rqi = jres['rqi']
            resp_topic = msg.topic.replace("oneM2M/req","oneM2M/resp")
            on_receive(jres['pc'])
            self.response_mqtt_notify(resp_topic,2001,'', origin, rqi,'')  # send Mobius ACK otherwise subscription is deleted
        except Exception as ex:
            traceback.print_exc()
        return 'OK'

    def response_mqtt_notify (self,rsp_topic, rsc, to, fr, rqi, inpc):
        global mqtt_silo_client
        rsp_message = {}
        rsp_message['m2m:rsp'] = {}
        rsp_message['m2m:rsp']['rsc'] = rsc
        rsp_message['m2m:rsp']['to'] = rsp_topic
        rsp_message['m2m:rsp']['fr'] = fr
        rsp_message['m2m:rsp']['rqi'] = rqi
        rsp_message['m2m:rsp']['pc'] = inpc
        mqtt_silo_client.publish(topic=rsp_topic, payload=json.dumps(rsp_message),qos=0)


class oneM2MHTTPSiloThread(Thread):
    def __init__(self):
        Thread.__init__(self)

    def run(self):
        global total_timestamp, samples
        print("Thread oneM2M data started")
        print("Mobius subscription" + " " + origin + " " + str(notification_URI) + " " + cnt_arn + " " + CSE_url)
        # notification topic actually is /oneM2M/req/Mobius/notify/json
        nuri = [notification_URI, "mqtt://127.0.0.1/notify"]
        status, sub = F4Im2m.sub_create(sub_rn, origin, nuri, "Mobius/" + cnt_arn, CSE_url)
        total_timestamp=0
        samples=0
        if status == 404:
            print(sub)
            sys.exit()
        time.sleep(0.05)
        app.run(host="0.0.0.0", port=int(urllib.parse.urlparse(notification_URI).port))

    
    @app.route('/notify', methods=['POST'])
    def recv_notify():
        jres = request.get_json()
        return on_receive(jres)

def on_receive(jres):
    global total_timestamp, samples
    received_timestamp = int(round(time.time() * (UNIT)))

    #print("enter notify, POST body: " + json.dumps(jres))
    try:
        if 'm2m:sgn' in jres:
            samples = samples + 1
            con = jres['m2m:sgn']['nev']['rep']['m2m:cin']['con']  # TODO could be a list?
            send_timestamp=con['value']['timestamp']
            msg_num = con['value']['sqn']
            delta_timestamp = received_timestamp - send_timestamp
            total_timestamp += delta_timestamp
            print("msg: %d, ∆ timestamp %.4f (ms), average: %.4f" % (msg_num, delta_timestamp, total_timestamp/samples))
            return 'OK', 201
        else:
            print("Bad notification format")
            return 'Bad notification format', 401
    except Exception as err:
        print("Bad notification format, error:", err)
        return 'Bad notification format', 401

def clean(signal, frame):
    global origin, cnt_arn, CSE_url, sub_rn
    # subscriptions delete
    subUri = "Mobius/" + cnt_arn + "/" + sub_rn
    print("deleting subscriptions, wait.....")
    F4Im2m.sub_delete(subUri, origin, CSE_url)
    time.sleep(1)
    os._exit(1)

if __name__ == '__main__':

    try:
        parser = argparse.ArgumentParser()
    
        parser.add_argument('-su', action='store', dest='serverURL', 
                            help='Mobius vSilo Server URL (default: http://172.17.0.5:7579) ', default='http://172.17.0.5:7579')
        parser.add_argument('-cnt', action='store', dest='cnt_arn', 
                            help='oneM2M container Absoulute Resource Name (default: relayTV:timestamp/urn:ngsi-ld:relayTV:timestamp/msg) ', default='relayTV:timestamp/urn:ngsi-ld:relayTV:timestamp/msg')
        parser.add_argument('-nuri', action='store', dest='notificationURI', 
                            help='Client URL where to receive notification (default http://172.17.0.1:5000/notify)', default='http://172.17.0.1:5000/notify')
        parser.add_argument('-m', action='store', dest='testMode', 
                            help='Test mode [HTTP, MQTT]: HTTP notification or MQTT notification (default HTTP)', default='HTTP')
        parser.add_argument('-v', action='store', dest='vThingID', 
                            help='vThingID (default: relayTV/timestamp) ', default='relayTV/timestamp')
        argcomplete.autocomplete(parser)
        args = parser.parse_args()

    except Exception:
        traceback.print_exc()
    
    CSE_url = args.serverURL
    tmp = args.vThingID.replace("/",":")
    cnt_arn = tmp + "/urn:ngsi-ld:"+tmp+"/msg"
    origin = "S"
    notification_URI = args.notificationURI
    sub_rn = "vSiloTestSub" 
    if (args.testMode == "MQTT"):
        oneM2M_MQTT_silo_thread = oneM2MMQTTSiloThread()
        oneM2M_MQTT_silo_thread.start()
    else:
        oneM2M_HTTP_silo_thread = oneM2MHTTPSiloThread()
        oneM2M_HTTP_silo_thread.start()


    time.sleep(2)
    signal.signal(signal.SIGINT, clean)
    while True:
        try:
            time.sleep(1)
        except Exception as err:
            print("Exception", err)
            time.sleep(1)
            os._exit(1)

