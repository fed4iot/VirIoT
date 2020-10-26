#!/usr/bin/python3

from flask import Flask
from flask import send_file
from flask import request, abort, Response, stream_with_context
import os
import json
import requests
import time
import paho.mqtt.client as mqtt
from threading import Thread

app = Flask(__name__)
flask_port = 5001
vStreams = {}

@app.route('/set-vthing-endpoint', methods=['POST'])
def set_vthing_endpoint(): 
    v_thing_name = request.json.get('vThingName', None)
    v_stream_endpoint = request.json.get('endpoint', None)
    vStreams[v_thing_name] = v_stream_endpoint
    return json.dumps({"message": "vthing registered successfully"}), 201

@app.route('/del-vthing-endpoint', methods=['POST'])
def del_vthing(): 
    v_thing_name = request.json.get('vThingName', None)
    if v_thing_name in vStreams.items():
        del vStreams[v_thing_name] 
    return json.dumps({"message": "vthing unregistered successfully"}), 201

@app.route("/<path:path>", methods=["GET"])
def proxy(path):
    # path[0] is the vThingName (not the ID) and identify the vThing within the ThingVisor. It is not forwarded to the upstream endpoint
    # return what GET from endpoint/path[1...] 
    found = False
    v_stream_endpoint = None
    for v_thing_name, v_stream_endpoint in vStreams.items():
        if path.startswith(v_thing_name+"/") or path == v_thing_name:
            found = True
            break
    if not found:
        return json.dumps({"message": "no vstream"}), 404
    if v_stream_endpoint is not None and v_stream_endpoint != 'dummy':
        uri = v_stream_endpoint+path.replace(v_thing_name, '')
        print(uri)
        new_headers = dict()
        for elem in request.headers:
            new_headers[elem[0]] = elem[1]
        new_headers.pop("Host", False)
        req = requests.get(uri, headers=new_headers, stream=True)
        response_headers = dict(req.headers)
        return Response(stream_with_context(req.iter_content(chunk_size=1024000)), headers=response_headers, status = req.status_code)
    elif v_stream_endpoint == 'dummy':
        path = "/app/dummy.txt"
        return send_file(path, as_attachment=True)
    else:
        return json.dumps({"message": "no vstream endpoint"}), 404

class httpThread(Thread):
    def __init__(self):
        Thread.__init__(self)

    def run(self):
        print("Thread Rx HTTP started")
        app.run(host='0.0.0.0', port=flask_port)
        print("Thread '" + self.name + " closed")

class mqttControlThread(Thread):

    # handler for mqtt control topics
    def __init__(self):
        Thread.__init__(self)
    
    def on_message_set_vthing_endpoint(self, jres):
        v_thing_name = jres['vThingID'].split("/",1)[1]
        v_stream_endpoint = jres['endpoint']
        vStreams[v_thing_name] = v_stream_endpoint
        print("Added endpoint "+v_thing_name+","+v_stream_endpoint)
        return
    
    def on_message_del_vthing_endpoint(self, jres):
        v_thing_name = jres['vThingID'].split("/",1)[1]
        del vStreams[v_thing_name]
        return

    def on_message_in_control_TV(self, mosq, obj, msg):
        payload = msg.payload.decode("utf-8", "ignore")
        print(msg.topic + " " + str(payload))
        jres = json.loads(payload.replace("\'", "\""))
        try:
            command_type = jres["command"]
            if command_type == "setVThingEndpoint":
                self.on_message_set_vthing_endpoint(jres)
            if command_type == "delVThingEndpoint":
                self.on_message_del_vthing_endpoint(jres)
        except Exception as ex:
            traceback.print_exc()
        return

    def run(self):
        print("Thread mqtt control started")
        global mqtt_control_client
        mqtt_control_client.connect(MQTT_control_broker_IP, MQTT_control_broker_port, 30)

        # Add message callbacks that will only trigger on a specific subscription match
        mqtt_control_client.message_callback_add(tv_control_prefix + "/" + thing_visor_ID + "/" + control_in_suffix,
                                                 self.on_message_in_control_TV)
        mqtt_control_client.subscribe(tv_control_prefix + "/" + thing_visor_ID + "/" + control_in_suffix)
        mqtt_control_client.loop_forever()
        print("Thread '" + self.name + "' terminated")

if __name__ == '__main__':
    
    thing_visor_ID = os.environ["thingVisorID"]
    parameters = os.environ["params"]
    
    MQTT_data_broker_IP = os.environ["MQTTDataBrokerIP"]
    MQTT_data_broker_port = int(os.environ["MQTTDataBrokerPort"])
    MQTT_control_broker_IP = os.environ["MQTTControlBrokerIP"]
    MQTT_control_broker_port = int(os.environ["MQTTControlBrokerPort"])

    # Mqtt settings
    tv_control_prefix = "TV"  # prefix name for controller communication topic
    v_thing_prefix = "vThing"  # prefix name for virtual Thing data and control topics
    data_out_suffix = "data_out"
    control_in_suffix = "c_in"
    control_out_suffix = "c_out"
    v_silo_prefix = "vSilo"

    mqtt_control_client = mqtt.Client()
    
    rxThread = httpThread()  # http server used to receive JSON messages from external producer
    rxThread.start()

    mqtt_control_thread = mqttControlThread()       # mqtt VirIoT control thread
    mqtt_control_thread.start()
    
    time.sleep(2)
    while True:
        try:
            time.sleep(3)
        except:
            print("KeyboardInterrupt")
            time.sleep(1)
            os._exit(1)
    