import argparse
import argcomplete
import sys
import traceback
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
import F4Ingsi
import logging
import csv
import datetime

UNIT = 10**3

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)
app = Flask(__name__)

# added by kenji for saving log (it is not good to define here)
pid = os.getpid()
log_name = './logs/consumer_orion_'+str(pid)+'.csv'
print (log_name)
####

class NGSIHTTPSiloThread(Thread):
    def __init__(self):
        Thread.__init__(self)

    def run(self):
        global total_timestamp, samples
        print("Thread NGSI data started")
        print("Broker subscription" + " " + str(notification_URI) + " " + entity_id_to_subscribe + " " + broker_url)
        status = F4Ingsi.subscribe_to_entity(broker_url, entity_id_to_subscribe, entity_type, notification_URI)
        total_timestamp=0
        samples=0
        if status == 404:
            print("Subscription failed. Exiting")
            sys.exit()
        time.sleep(0.05)
        app.run(host="0.0.0.0", port=int(urllib.parse.urlparse(notification_URI).port))

    
    @app.route('/notify', methods=['POST'])
    def recv_notify():
        jres = request.get_json()
        return on_receive(jres)

def on_receive(jres):
    global total_timestamp, samples, subscriptionID, csvFile
    now_timestamp = int(round(time.time() * (UNIT)))

    print("enter notify, POST body: " + json.dumps(jres))
    try:
        if 'data' in jres:

            if 'subscriptionId' in jres: 
                subscriptionID = jres['subscriptionId']

            # added by kenji for saving log
            log_timestamp = datetime.datetime.now()
            #####

            samples = samples + 1

            con = jres['data'][0]['msg']
            send_timestamp = con['value']['timestamp']
            msg_num = con['value']['sqn']
            
            delta_timestamp = now_timestamp - send_timestamp
            total_timestamp += delta_timestamp
            print("msg: %d, delta timestamp %.4f (ms), average: %.4f" % (msg_num, delta_timestamp, total_timestamp/samples))

            # added by kenji for saving log
            with open(log_name, 'a') as f:
                writer = csv.writer(f)
                writer.writerow([str(log_timestamp), 'orion', msg_num, delta_timestamp, total_timestamp/samples])
            ######

            if csvFile is not None:
                csvFile.write("%d \t %.4f \t %.4f \n" % (msg_num, delta_timestamp, self.total_timestamp/self.samples))
                csvFile.flush()
            return 'OK', 201
        else:
            print("Bad notification format")
            return 'Bad notification format', 401
    except Exception as err:
        print("Bad notification format, error:", err)
        return 'Bad notification format', 401

def clean(signal, frame):
    
    global broker_url, subscriptionID, entity_id_to_subscribe
    # subscriptions delete
    print("deleting subscriptions, wait.....")
    F4Ingsi.delete_subscription_to_entity(broker_url, subscriptionID, entity_id_to_subscribe)
    time.sleep(1)
    os._exit(1)

if __name__ == '__main__':

    try:
        parser = argparse.ArgumentParser()
    
        parser.add_argument('-s', action='store', dest='serverIP', 
                            help='Broker vSilo Server IP (default: 172.17.0.5) ', default='172.17.0.5')
        parser.add_argument('-p', action='store', dest='serverPort', 
                            help='Broker vSilo Server HTTP Port (default: 1026) ', default='1026')
        parser.add_argument('-nuri', action='store', dest='notificationURI', 
                            help='Client HTTP URL where to receive notification (default http://172.17.0.1:5000/notify)', default='http://172.17.0.1:5000/notify')
        parser.add_argument('-v', action='store', dest='vThingID', 
                            help='vThingID (default: relay/vThingRelay) ', default='relay/vThingRelay')
        parser.add_argument('-t', action='store', dest='vThingType', 
                            help='vThingType (default: message) ', default='message')
        parser.add_argument('-f', action='store', dest='csvFileName', 
                            help='csvFile (default: None) ', default=None)                            
        argcomplete.autocomplete(parser)
        args = parser.parse_args()

    except Exception:
        traceback.print_exc()
    
    broker_url = "http://"+args.serverIP+":"+args.serverPort
    tmp = args.vThingID.replace("/",":")
    entity_id_to_subscribe = "urn:ngsi-ld:"+tmp
    entity_type = args.vThingType
    notification_URI = args.notificationURI
    
    csvFileName = args.csvFileName
    csvFile=None
    if csvFileName is not None:
        csvFile =  open(csvFileName, "w")

    subscriptionID = ""

    NGSI_HTTP_silo_thread = NGSIHTTPSiloThread()
    NGSI_HTTP_silo_thread.start()

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

