#!/usr/bin/python3

from flask import Flask,request,redirect,Response,stream_with_context,abort
import requests
import os
import sys
import time
import signal
import traceback
import paho.mqtt.client as mqtt
import json
import re
from threading import Thread
from pymongo import MongoClient
from bson.json_util import dumps


regex=re.compile('^[a-z0-9](?:[a-z0-9\-]{0,61}[a-z0-9])?')
SVC_SUFFIX = ".default.svc.cluster.local"
# MQTT settings
v_silo_prefix = "vSilo"  # prefix name for virtual IoT System communication topic
v_thing_prefix = "vThing"  # prefix name for virtual Thing data and control topics
v_thing_data_suffix = "data_out"
in_control_suffix = "c_in"
out_control_suffix = "c_out"

mqtt_virIoT_control_client = mqtt.Client()
mqtt_virIoT_data_client = mqtt.Client()


proxies = {
        "http": "http://viriot-nginx.default.svc.cluster.local",
}
vThingList = list()


class MqttControlThread(Thread):
    def __init__(self):
        Thread.__init__(self)

    def run(self):
        mqtt_virIoT_control_client.connect(
            virIoT_mqtt_control_broker_IP, virIoT_mqtt_control_broker_port, 10)
        # Add message callbacks that will only trigger on a specific subscription match
        mqtt_virIoT_control_client.message_callback_add(v_silo_prefix + "/" + v_silo_id + "/" + in_control_suffix,
                                                        on_in_control_msg)
        mqtt_virIoT_control_client.subscribe(
            v_silo_prefix + "/" + v_silo_id + "/" + in_control_suffix)
        print("Thread mqtt_virIoT_control_client started")
        mqtt_virIoT_control_client.loop_forever()
        print("Thread mqtt_virIoT_data_client terminated")


class proxy_thread(Thread):
    global SVC_SUFFIX, vThingList
    app = Flask(__name__)
    
    def __init__(self):
        Thread.__init__(self)
        #logging.basicConfig(level=logging.INFO)
        #self.app.run(host=flask_host, port=flask_port)
    
    def run(self):
        self.app.run(host = "0.0.0.0", debug = False,port=80) 
    
    
    @app.route("/vstream/<path:path>",methods=["GET"])
    def proxy(path):
        global SVC_SUFFIX
        path_parts= path.split("/",1)
        if len(path_parts)<1:
            abort(404) 
        vThingID = path_parts[0]
        if vThingID not in vThingList:
            abort(404) 
        if request.method=="GET":
            uri = "http://"+vThingID+SVC_SUFFIX+"/"+"".join(path_parts[1:])
            print(uri)
            req = requests.get(uri, stream=True, proxies=proxies)
            return Response(stream_with_context(req.iter_content(chunk_size=1024000)), content_type = req.headers['content-type'])

# topic messages
def on_in_control_msg(mosq, obj, msg):
    payload = msg.payload.decode("utf-8", "ignore")
    print(msg.topic + " " + str(payload))
    jres = json.loads(payload.replace("\'", "\""))
    try:
        commandType = jres["command"]
        if commandType == "addVThing":
            on_message_add_vThing(jres)
            return "creating vThing"
        elif commandType == "deleteVThing":
            on_message_delete_vThing(jres)
            return "deleting vThing"
        else:
            return "invalid command"
    except Exception as ex:
        traceback.print_exc()
        return 'invalid command'


def on_message_add_vThing(jres):
    # print("on_message_add_vThing")
    try:
        v_thing_id = jres['vThingID']
        res = vThingList.append(v_thing_id.replace("/","-").replace("_","-").replace(".","-").lower())
        print(vThingList)
        if res:
            # add subscription for virtual Thing control topic (on mqtt control client)
            mqtt_virIoT_control_client.subscribe(
                v_thing_prefix + '/' + v_thing_id + '/' + out_control_suffix)
            mqtt_virIoT_control_client.message_callback_add(v_thing_prefix + '/' + v_thing_id + '/' + out_control_suffix,
                                                            on_vThing_out_control)
            return 'OK'
        else:
            return 'Creation fails'
    except Exception as ex:
        traceback.print_exc()
        return 'ERROR'


def on_message_delete_vThing(jres):
    print("on_message_delete_vThing")
    try:
        v_thing_id = jres['vThingID']
        res = vThingList.delete(v_thing_id.replace("/","-").replace("_","-").replace(".","-").lower())
        # removing mqtt subscriptions and callbacks
        mqtt_virIoT_control_client.message_callback_remove(
            v_thing_prefix + '/' + v_thing_id + '/out_control')
        mqtt_virIoT_control_client.unsubscribe(
            v_thing_prefix + '/' + v_thing_id + '/out_control')
        delete_vThing_on_Broker(jres)

    except Exception:
        traceback.print_exc()
        return 'ERROR'

def on_vThing_out_control(mosq, obj, msg):
    print("on_vThing_out_control")
    payload = msg.payload.decode("utf-8", "ignore")
    jres = json.loads(payload.replace("\'", "\""))
    if jres["command"] == "deleteVThing":
        msg = {"vThingID": jres["vThingID"]}
        on_message_delete_vThing(msg)
    else:
        # TODO manage others commands
        return 'command not managed'
    return 'OK'


def restore_virtual_things():
    # Retrieve from system db the list of virtual thing in use and restore them
    # needed in case of silo controller restart
    db_client = MongoClient('mongodb://' + db_IP + ':' + str(db_port) + '/')
    db = db_client[db_name]
    connected_v_things = json.loads(
        dumps(db[v_thing_collection].find({"vSiloID": v_silo_id}, {"vThingID": 1, "_id": 0})))
    if len(connected_v_things) > 0:
        for vThing in connected_v_things:
            if "vThingID" in vThing:
                print("restoring virtual thing with ID: " + vThing['vThingID'])
                on_message_add_vThing(vThing)


def handler(signal, frame):
    sys.exit()

def dns_subdomain_converter(s):
    s = s.lower()
    ls = list(s)
    while True:
        last=regex.match(s).span()[1]
        if last == len(s):
            break
        ls[last]='-'
        s=''.join(ls)
    return(s)


signal.signal(signal.SIGINT, handler)


if __name__ == '__main__':

    # -------------- DEBUG PARAMETERS --------------
    # tenant_id = "tenant1"
    # flavourParams = []
    # v_silo_id = "tenant1_Silo2"
    # virIoT_mqtt_data_broker_IP = "127.0.0.1"
    # virIoT_mqtt_data_broker_port = 1883
    # virIoT_mqtt_control_broker_IP = "127.0.0.1"
    # virIoT_mqtt_control_broker_port = 1883
    # db_IP = "172.17.0.2"
    # db_port = 27017

    MAX_RETRY = 3
    v_silo_id = os.environ["vSiloID"]
    db_IP = os.environ['systemDatabaseIP']  # IP address of system database
    db_port = os.environ['systemDatabasePort']  # port of system database

    # Mongodb settings
    time.sleep(1.5)  # wait before query the system database
    db_name = "viriotDB"  # name of system database
    v_thing_collection = "vThingC"
    v_silo_collection = "vSiloC"
    db_client = MongoClient('mongodb://' + db_IP + ':' + str(db_port) + '/')
    db = db_client[db_name]
    silo_entry = db[v_silo_collection].find_one({"vSiloID": v_silo_id})

    valid_silo_entry = False
    for x in range(MAX_RETRY):
        if silo_entry is not None:
            valid_silo_entry = True
            break
        time.sleep(3)

    if not valid_silo_entry:
        print("Error: Virtual Silo entry not found for v_silo_id:", v_silo_id)
        exit()

    try:
        # read paramenters from DB
        tenant_id = silo_entry["tenantID"]
        flavourParams = silo_entry["flavourParams"]  # in this flavour, param is the silo type (Raw, Mobius, FiWare)

        virIoT_mqtt_data_broker_IP = silo_entry["MQTTDataBroker"]["ip"]
        virIoT_mqtt_data_broker_port = int(silo_entry["MQTTDataBroker"]["port"])
        virIoT_mqtt_control_broker_IP = silo_entry["MQTTControlBroker"]["ip"]
        virIoT_mqtt_control_broker_port = int(silo_entry["MQTTControlBroker"]["port"])

    except Exception as e:
        print("Error: Parameters not found in silo_entry", e)
        exit()

    db_client.close()  # Close DB connection
    print("starting silo controller")

    v_silo_prefix = "vSilo"  # prefix name for virtual IoT System communication topic
    v_thing_prefix = "vThing"  # prefix name for virtual Thing data and control topics
    data_out_suffix = "data_out"
    data_in_suffix = "data_in"
    control_in_suffix = "c_in"
    control_out_suffix = "c_out"

    # Mongodb settings
    db_name = "viriotDB"  # name of system database
    v_thing_collection = "vThingC"

    virIoT_proxy_broker_thread = proxy_thread()
    virIoT_proxy_broker_thread.start()
    #virIoT_mqtt_data_thread = MqttDataThread()
    #virIoT_mqtt_data_thread.start()
    virIoT_mqtt_control_thread = MqttControlThread()
    virIoT_mqtt_control_thread.start()

    # restore virtual things found in the systemDB. It is useful after vSilo crash and restore (e.g. by k8s)
    restore_virtual_things()

    while True:
        try:
            time.sleep(3)
        except:
            print("KeyboardInterrupt"+"\n")
            time.sleep(1)
            os._exit(1)
