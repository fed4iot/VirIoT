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
import kafka
from threading import Thread
from flask import Flask
from flask import json
from flask import request
import signal
import F4Im2m
import logging
import csv
import datetime
import ast

UNIT = 10**3

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)
app = Flask(__name__)

# added by kenji for saving log (it is not good to define here)
pid = os.getpid()
log_name = './logs/consumer_mobius2_'+str(pid)+'.csv'
print (log_name)
####

kafka_broker = ""
data_topic = "cbpf_to_exporter"
prev_data = ""
TIMEOUT = 10

class oneM2MMQTTSiloThread(Thread):
    def __init__(self):
        Thread.__init__(self)


    def run(self):
        global total_timestamp, samples, mqtt_silo_client
        print("Thread oneM2M data started")
        print("Mobius subscription for " + cnt_arn + " on " + CSE_url)
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
        mqtt_silo_client.connect(urllib.parse.urlparse(CSE_url).hostname, int(MQTT_port), 30)
        mqtt_silo_client.message_callback_add(topic, self.on_receive_MQTT)
        mqtt_silo_client.subscribe(topic)
        mqtt_silo_client.loop_forever()
        print("Thread '" + self.name + "' terminated")

    def on_receive_MQTT(self,mosq, obj, msg):
        payload = msg.payload.decode("utf-8", "ignore")
        #print (payload)
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
    global total_timestamp, samples, csvFile, data_broker, data_topic, prev_data
    received_timestamp = int(round(time.time() * (UNIT)))

    #print("enter notify, POST body: " + json.dumps(jres))
    try:
        if 'm2m:sgn' in jres:

            # added by kenji for saving log
            log_timestamp = datetime.datetime.now()
            #####

            samples = samples + 1
            con = str(jres['m2m:sgn']['nev']['rep']['m2m:cin']['con'])
            dict_con = ast.literal_eval(con)
            #con = json.loads(jres['m2m:sgn']['nev']['rep']['m2m:cin']['con'])
            print (json.dumps(dict_con, indent=2))

            if (prev_data != dict_con):
                print ("publish to logger")
                data_broker.send(data_topic, json.dumps(dict_con).encode('utf-8'))
                prev_data = dict_con
            else:
                pass

            #con = jres['m2m:sgn']['nev']['rep']['m2m:cin']['con']
            #send_timestamp = con['value']['timestamp']
            #msg_num = con['value']['sqn']
            
            #delta_timestamp = received_timestamp - send_timestamp
            #total_timestamp += delta_timestamp

            # added by kenji for saving log
            #with open(log_name, 'a') as f:
            #    writer = csv.writer(f)
            #    writer.writerow([str(log_timestamp), 'mobius2', msg_num, delta_timestamp, total_timestamp/samples])
            ######

            #print("msg: %d, delta timestamp %.4f (ms), average: %.4f" % (msg_num, delta_timestamp, total_timestamp/samples))
            #if csvFile is not None:
            #    csvFile.write("%d \t %.4f \t %.4f \n" % (msg_num, delta_timestamp, self.total_timestamp/self.samples))
            #    csvFile.flush()
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
    
        parser.add_argument('-s', action='store', dest='serverIP', 
                            help='Mobius vSilo Server IP (default: 172.17.0.5) ', default='172.17.0.5')
        parser.add_argument('-p', action='store', dest='serverPort', 
                            help='Mobius vSilo Server HTTP Port (default: 7579) ', default='7579')
        parser.add_argument('-pm', action='store', dest='serverMQTTPort', 
                            help='Mobius vSilo Server MQTT Port (default: 1883) ', default='1883')
        parser.add_argument('-nuri', action='store', dest='notificationURI', 
                            help='Client HTTP URL where to receive notification (default http://172.17.0.1:5000/notify) in case of HTTP mode', default='http://172.17.0.1:5000/notify')
        parser.add_argument('-m', action='store', dest='testMode', 
                            help='Test mode [HTTP, MQTT]: HTTP notification or MQTT notification (default HTTP)', default='HTTP')
        parser.add_argument('-v', action='store', dest='vThingID', 
                            help='vThingID (default: relay-tv/timestamp) ', default='relay-tv/timestamp')
        parser.add_argument('-f', action='store', dest='csvFileName', 
                            help='csvFile (default: None) ', default=None) 
        argcomplete.autocomplete(parser)
        args = parser.parse_args()

    except Exception:
        traceback.print_exc()
    
    CSE_url = "http://"+args.serverIP+":"+args.serverPort
    MQTT_port = args.serverMQTTPort
    tmp = args.vThingID.replace("/",":")
    cnt_arn = tmp + "/" + tmp + "/msg"
    origin = "S"
    notification_URI = args.notificationURI
    sub_rn = "vSiloTestSub" 
    

    data_broker = kafka.KafkaProducer(bootstrap_servers=kafka_broker,
            max_request_size=15728640, api_version_auto_timeout_ms=int(TIMEOUT))


    csvFileName = args.csvFileName
    csvFile=None
    if csvFileName is not None:
        csvFile =  open(csvFileName, "w")

    if (args.testMode == "MQTT"):
        print("MQTT test mode")
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
            if csvFile is not None:
                csvFile.close()
            time.sleep(1)
            os._exit(1)

