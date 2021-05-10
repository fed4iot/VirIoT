# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# Fed4IoT thingVisor generic

import time
import os
import random
import json
import base64
import traceback
import paho.mqtt.client as mqtt
from threading import Thread
from pymongo import MongoClient
from context import Context
from concurrent.futures import ThreadPoolExecutor
import requests

##### CUSTOMIZE generic TV imports
import redis
rdis = redis.Redis(unix_socket_path="/app/redis/redis.sock")
buffername = "bufferofframes"

from flask import Flask, request, Response
app=Flask(__name__)


@app.route('/currentframe/<randomid>')
def GET_current_frame_by_id(randomid):
    global rdis
    global buffername
    ### i could offer the img_str buffer via HTTP at this point
    headers={"Content-disposition": "attachment"}
    headers["Cache-Control"]="no-cache"
    print("GET ", randomid)

    try:
        # get from the redis stream named "buffername" just 1 item (from randomid to randomid)
        list_of_matching_results = rdis.xrange(buffername,randomid,randomid)
        # we get back a list of results (with only 1 result). we pick it
        first_result = list_of_matching_results[0]
        # each result is a tuple where first element [0] is the id (key),
        # second element [1] is the dict (value) holding the frame information
        frame_information = first_result[1]
        data = frame_information[b"data"]
        observedAt = frame_information[b"observedAt"]
    except:
        data = ""

    return Response(data, mimetype='image/jpeg', headers=headers)


@app.route('/framesinput',methods=['POST'])            
def POST_frames():
    global rdis
    global buffername
    print(request.files)
    print(type(request.files))
    print(len(request.files))
    for keys,values in request.files.items():
        print(keys)
        print(values)
    uploaded_cameraframe = request.files.get("file")
    metadata = json.load(request.files.get("json"))
    data = uploaded_cameraframe.read()
    # Redis client instances can safely be shared between threads.
    # Internally, connection instances are only retrieved from the connection
    # pool during command execution, and returned to the pool directly after.
    # Command execution never modifies state on the client instance.
    # We keep at most 20 images in the buffer
    id = rdis.xadd(buffername, {"data":data, "observedAt":metadata["observedAt"]}, maxlen=20, approximate=True)

    print("Pushed to redis ", id)
    return 'success'
##### END GLOBAL CUSTOMIZE generic TV


def publish_entities_of_this_vthing(entities):
    for entity in entities:
        for property in entity.properties:
            entity={
                "@context": [
                    "https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld"
                ],
                "id": "urn:ngsi-ld:CameraBotPicture:"+str(index),
                "type": "CameraBotPicture",
                "link_to_picture": {
                    "type": "Property",
                    "value": "/cameras/"+str(index)+"/image"
                },
                "timestamp": {
                    "type": "Property",
                    "value": "0"
                }
            }

            if 'timestamp' in rdata:
                entity['timestamp']['value']=rdata['timestamp']

            message = {"data": [entity], "meta": {"vThingID": v_thing_ID[index]}}
            future = executor.submit(send_message, message, index)


    return

# function for publishing messages through mqtt on the vthing's data out topic
def publish_to_vthing_data_out_topic(message):
    print("topic name: " + v_thing['topic'] + '/' + out_data_suffix + ", message: " + json.dumps(message))
    mqtt_data_client.publish(v_thing['topic'] + '/' + out_data_suffix,
                                json.dumps(message))  # publish received data to data topic by using neutral format

def create_vthing(name, type, commands):
    v_thing['name']=name
    v_thing['type_attr']=type
    v_thing['ID']=thing_visor_ID + "/" + name
    v_thing['label']=name
    v_thing['description']="generic virtual thing"
    v_thing['v_thing']={
        "label": v_thing['label'],
        "id": v_thing['ID'],
        "description": v_thing['description']
    }

    v_thing['ID_LD']="urn:ngsi-ld:"+thing_visor_ID+":" + v_thing['name']

    # create and save the Context for the new vThing
    # Context is a "map" of current virtual thing state
    v_thing['context']=Context()

    # set topic the name of mqtt topic on witch publish vThing data
    # e.g. vThing/helloWorld/hello
    v_thing['topic']=v_thing_prefix + "/" + v_thing['ID']

    # set the commands array for the vThing
    v_thing['commands']=commands


def get_vthing_name(name):
    name=name.split(':')[-1]
    return name

def get_silo_name(nuri):
    return nuri.split('/')[-2]

class mqttDataThread(Thread):
    # Class used to:
    # 1) handle actuation command workflow
    # 2) publish actuator status when it changes
    global mqtt_data_client, context_list, executor, commands

    def send_commandResult(self, cmd_name, cmd_info, id_LD, payload):
        try:  
            pname = cmd_name+"-result"
            pvalue = cmd_info.copy()
            pvalue['cmd-result'] = payload
            ngsiLdEntityResult = {"id": id_LD,
                                    "type": v_thing['type_attr'],
                                    pname: {"type": "Property", "value": pvalue},
                                    "@context": [ "https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld" ]
                                    }
            data = [ngsiLdEntityResult]
            message = {"data": data, "meta": {
                "vThingID": v_thing['ID']
            }}  # neutral-format message

            if "cmd-nuri" in cmd_info:
                if cmd_info['cmd-nuri'].startswith("viriot://"):
                    topic = cmd_info['cmd-nuri'][len("viriot://"):]
                    self.publish(message, topic)
                else:
                    self.publish(message, v_thing['topic'])
            else:
                self.publish(message, v_thing['topic'])
        except:
            traceback.print_exc()

    def send_commandStatus(self, cmd_name, cmd_info, id_LD, status_code):
        try:  
            pname = cmd_name+"-status"
            pvalue = cmd_info.copy()
            pvalue['cmd-status'] = status_code
            ngsiLdEntityStatus = {"id": id_LD,
                                    "type": v_thing['type_attr'],
                                    pname: {"type": "Property", "value": pvalue},
                                    "@context": [ "https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld" ]
                                    }
            data = [ngsiLdEntityStatus]
            message = {"data": data, "meta": {
                "vThingID": v_thing['ID']
            }}  # neutral-format message
            
            if "cmd-nuri" in cmd_info:
                if cmd_info['cmd-nuri'].startswith("viriot://"):
                    topic = cmd_info['cmd-nuri'][len("viriot://"):]
                    self.publish(message, topic)
                else:
                    self.publish(message, v_thing['topic'])
            else:
                self.publish(message, v_thing['topic'])
        except:
            traceback.print_exc()

    def receive_commandRequest(self, cmd_entity):
        try:
            id_LD = cmd_entity["id"]
            for cmd_name in v_thing['commands']:
                if cmd_name in cmd_entity:
                    cmd_info = cmd_entity[cmd_name]['value']
                    fname = cmd_name.replace('-','_')
                    fname = "on_"+fname
                    f=getattr(self,fname)
                    if "cmd-qos" in cmd_info:
                        if int(cmd_info['cmd-qos']) == 2:
                            self.send_commandStatus(cmd_name, cmd_info, id_LD, "PENDING")
                    executor.submit(f, cmd_name, cmd_info, id_LD, self)
        except:
            traceback.print_exc()

    def on_GENERIC_COMMAND(self, cmd_name, cmd_info, id_LD, actuatorThread):
        # do things
        # ...

        # publish command result
        if "cmd-qos" in cmd_info:
            if int(cmd_info['cmd-qos']) > 0:
                self.send_commandResult(cmd_name, cmd_info, id_LD, "ok")
    
    def publish(self, message, out_topic):
        msg=json.dumps(message)

        # publish data to out_topic
        mqtt_data_client.publish(out_topic, msg)

        print("Message sent on "+out_topic + "\n" + msg+"\n")

    def on_message_data_in_vThing(self, mosq, obj, msg):
        payload = msg.payload.decode("utf-8", "ignore")
        print("Message received on "+msg.topic + "\n" + payload+"\n")
        jres = json.loads(payload.replace("\'", "\""))
        try:
            data = jres["data"]
            for entity in data:
                id_LD = entity["id"]
                for cmd in v_thing['commands']:
                    if cmd in entity:
                        self.receive_commandRequest(entity)
                        continue
        except:
            traceback.print_exc()


    # mqtt client for sending data
    def __init__(self):
        Thread.__init__(self)

    def run(self):
        print("Thread mqtt data started")
        global mqtt_data_client
        mqtt_data_client.connect(MQTT_data_broker_IP, MQTT_data_broker_port, 30)

        self.create_vthing()

        mqtt_data_client.loop_forever()
        print("Thread '" + self.name + "' terminated")

    def create_vthing(self):
        ngsiLdEntity = {"id": v_thing['ID_LD'],
            "type": v_thing['type_attr'],
            "commands": {"type": "Property", "value": v_thing['commands']},
            "@context": [ "https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld" ]
        }
        data = [ngsiLdEntity]
        v_thing['context'].set_all(data)

        mqtt_data_client.message_callback_add(v_thing['topic'] + "/" + in_data_suffix,
                                            self.on_message_data_in_vThing)
        # Subscribe mqtt_data_client to the vThing topic
        mqtt_data_client.subscribe(
            v_thing['topic'] + "/" + in_data_suffix)


class MqttControlThread(Thread):
    def on_message_get_thing_context(self, jres):
        silo_id = jres["vSiloID"]
        message = {"command": "getContextResponse", "data": v_thing['context'].get_all(), "meta": {"vThingID": v_thing['ID']}}
        mqtt_control_client.publish(v_silo_prefix + "/" + silo_id + "/" + in_control_suffix, json.dumps(message))

    def send_destroy_v_thing_message(self):
        msg = {"command": "deleteVThing", "vThingID": v_thing['ID'], "vSiloID": "ALL"}
        mqtt_control_client.publish(v_thing_prefix + "/" + v_thing['ID'] + "/" + out_control_suffix, json.dumps(msg))

    def send_destroy_thing_visor_ack_message(self):
        msg = {"command": "destroyTVAck", "thingVisorID": thing_visor_ID}
        mqtt_control_client.publish(tv_control_prefix + "/" + thing_visor_ID + "/" + out_control_suffix, json.dumps(msg))

    def on_message_destroy_thing_visor(self, jres):
        global db_client
        db_client.close()
        self.send_destroy_v_thing_message()
        self.send_destroy_thing_visor_ack_message()
        print("Shutdown completed")

    def on_message_update_thing_visor(self, jres):
        global sample_par

        print("Print update_info:", jres['update_info'])
        if 'sample_par' in jres['params']:
            sample_par=jres['params']['sample_par']

    # handler for mqtt control topics
    def __init__(self):
        Thread.__init__(self)

    def on_message_in_control_vThing(self, mosq, obj, msg):
        payload = msg.payload.decode("utf-8", "ignore")
        print(msg.topic + " " + str(payload))
        jres = json.loads(payload.replace("\'", "\""))
        try:
            command_type = jres["command"]
            if command_type == "getContextRequest":
                self.on_message_get_thing_context(jres)
        except:
            traceback.print_exc()

    def on_message_in_control_TV(self, mosq, obj, msg):
        payload = msg.payload.decode("utf-8", "ignore")
        jres = json.loads(payload)
        print(msg.topic + " " + str(jres))
        try:
            command_type = jres["command"]
            if command_type == "destroyTV":
                self.on_message_destroy_thing_visor(jres)
            elif command_type == "updateTV":
                self.on_message_update_thing_visor(jres)
        except:
            traceback.print_exc()
        return 'invalid command'

    def run(self):
        print("Thread mqtt control started")
        global mqtt_control_client
        mqtt_control_client.connect(MQTT_control_broker_IP, MQTT_control_broker_port, 30)

        self.create_vthing()

        # Add message callbacks that will only trigger on a specific subscription match
        mqtt_control_client.message_callback_add(tv_control_prefix + "/" + thing_visor_ID + "/" + in_control_suffix,
                                                 self.on_message_in_control_TV)
        mqtt_control_client.subscribe(tv_control_prefix + "/" + thing_visor_ID + "/" + in_control_suffix)

        mqtt_control_client.loop_forever()
        print("Thread '" + self.name + "' terminated")
    
    def create_vthing(self):
        # Publish on the thingVisor out_control topic the createVThing command and other parameters
        v_thing_message = {"command": "createVThing",
                        "thingVisorID": thing_visor_ID,
                        "vThing": v_thing['v_thing']}
        mqtt_control_client.publish(tv_control_prefix + "/" + thing_visor_ID + "/" + out_control_suffix,
                                    json.dumps(v_thing_message))

        # Add message callbacks that will only trigger on a specific subscription match
        mqtt_control_client.message_callback_add(v_thing['topic'] + "/" + in_control_suffix,
                                                self.on_message_in_control_vThing)
        mqtt_control_client.subscribe(v_thing['topic'] + '/' + in_control_suffix)

# main
if __name__ == '__main__':
    MAX_RETRY = 3
    thing_visor_ID = os.environ["thingVisorID"]

    # Mongodb settings
    time.sleep(1.5)  # wait before query the system database
    db_name = "viriotDB"  # name of system database
    thing_visor_collection = "thingVisorC"
    db_IP = os.environ['systemDatabaseIP']  # IP address of system database
    db_port = os.environ['systemDatabasePort']  # port of system database
    db_client = MongoClient('mongodb://' + db_IP + ':' + str(db_port) + '/')
    db = db_client[db_name]
    tv_entry = db[thing_visor_collection].find_one({"thingVisorID": thing_visor_ID})

    valid_tv_entry = False
    for x in range(MAX_RETRY):
        if tv_entry is not None:
            valid_tv_entry = True
            break
        time.sleep(3)

    if not valid_tv_entry:
        print("Error: ThingVisor entry not found for thing_visor_ID:", thing_visor_ID)
        exit()

    try:
        # import paramenters from DB
        MQTT_data_broker_IP = tv_entry["MQTTDataBroker"]["ip"]
        MQTT_data_broker_port = int(tv_entry["MQTTDataBroker"]["port"])
        MQTT_control_broker_IP = tv_entry["MQTTControlBroker"]["ip"]
        MQTT_control_broker_port = int(tv_entry["MQTTControlBroker"]["port"])

        parameters = tv_entry["params"]
        if parameters:
            params = json.loads(parameters)
        else:
            params={}

    except json.decoder.JSONDecodeError:
        print("error on params (JSON) decoding" + "\n")
        exit()
    except Exception as e:
        print("Error: Parameters not found in tv_entry", e)
        exit()

    # store parameters in some variables
    v_thing_name="sample"
    v_thing_type="Sample"

    if params:
        if 'v_thing_name' in params:
            v_thing_name = params['v_thing_name']
        if 'v_thing_type' in params:
            v_thing_type = params['v_thing_type']

    # mqtt settings
    tv_control_prefix = "TV"  # prefix name for controller communication topic
    v_thing_prefix = "vThing"  # prefix name for virtual Thing data and control topics
    in_control_suffix = "c_in"
    out_control_suffix = "c_out"
    out_data_suffix = "data_out"
    in_data_suffix = "data_in"
    v_silo_prefix = "vSilo"

    port_mapping = db[thing_visor_collection].find_one({"thingVisorID": thing_visor_ID}, {"port": 1, "_id": 0})
    print("port mapping: " + str(port_mapping))

    # create the sample vThing
    v_thing={}
    create_vthing(v_thing_name,v_thing_type,["GENERIC_COMMAND"])

    mqtt_control_client = mqtt.Client()
    mqtt_data_client = mqtt.Client()

    # threadPoolExecutor of size one to handle one command at a time in a fifo order
    executor = ThreadPoolExecutor(1)

    mqtt_control_thread = MqttControlThread()  # mqtt control thread
    mqtt_control_thread.start()

    mqtt_data_thread = mqttDataThread()  # mqtt data thread
    mqtt_data_thread.start()

##### CUSTOMIZE generic TV
    print("v_thing_name: " + str(v_thing_name))
    print("v_thing_type: " + str(v_thing_type))
    print()
##### decide here to start flask or not, and in that case the main thread
##### block with flask
    # starting flask
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
