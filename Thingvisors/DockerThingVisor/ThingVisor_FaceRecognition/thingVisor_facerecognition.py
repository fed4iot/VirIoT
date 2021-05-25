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

# Fed4IoT Thing ThingVisor hello world

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

from eve import Eve
from flask import request, Response

from eve.io.base import BaseJSONEncoder
from eve.io.mongo import Validator
from eve.methods.post import post_internal
from eve.methods.delete import deleteitem_internal

import constants

import requests
import uuid
import magic


# -*- coding: utf-8 -*-

# This TV creates just one vthing hardcoded name "detector". If the TV is named "facerec-tv", then:
# the vthing ID is: facerec-tv/detector, and the vthing produces a stream of one NGSI-LD entity,
# which has NGSI-LD identifier: urn:ngsi-ld:facerec-tv:detector, and the NGSI-LD type of the
# produced entity is hardcoded to: FaceDetector
# The vthing supports the following commands: ["start","stop","set-face-feature","delete-by-name"].
# Users interact with the vthing by actuating it, i.e. sending commands.
# A target face to be recognized cannot be embedded into a command, hence the set-face-feature command

app = Eve()


def on_post_PATCH_faceInput(request,lookup):
    try:
        data=json.loads(lookup.get_data())

        if '_id' in data:
            id=data['_id']
            name=image_to_name_mapping[id]

            print("")
            print("Image patched on "+id)
            print("")

            # get image
            faceInput = app.data.driver.db['faceInput']
            a = faceInput.find_one({'_id':id})
            image=app.media.get(a['image'])

            # send all data to the camera system
            _camera_ip, _camera_port=get_camera_ip_port()
            payload = {'name':name,'id':id}
            files={'image':image}
            res=requests.post("http://"+_camera_ip+':'+_camera_port+'/images', data=payload, files=files)

            # check response
            if res.status_code>=400:
                print("Error when posting to the camera system: "+str(res.status_code))
                return 
    except:
        traceback.print_exc()


def on_post_POST_faceOutput(request,lookup):
    try:
        data=json.loads(lookup.get_data())

        if '_id' in data:
            id=request.form['id']
            name=image_to_name_mapping[id]

            print("")
            print("Status changed for person "+name)
            print("New status: "+str(request.form['result']))
            print("")

            # send new command status
            # to inform that the person status has changed
            payload={
                "status": request.form['result'],
                "name": name,
                "count": image_count[name],
                "timestamp": request.form['timestamp'],
                "link_to_base_image": "/faceInput/"+id+"/image",
                "link_to_current_image": "/faceOutput/"+data['_id']+"/image"
            }

            mqtt_data_thread.publish_actuation_commandStatus_message(
                command_data[id]['cmd_name'],
                command_data[id]['cmd_info'],
                command_data[id]['id_LD'],
                payload
            )
    except:
        traceback.print_exc()

    
def on_start(self, cmd_name, cmd_info, id_LD, actuatorThread):
    print("Sending start command to camera system")

    _camera_ip, _camera_port=get_camera_ip_port()
    res=requests.get("http://"+_camera_ip+':'+_camera_port+'/start')

    # publish command result
    if "cmd-qos" in cmd_info:
        if int(cmd_info['cmd-qos']) > 0:
            self.send_commandResult(cmd_name, cmd_info, id_LD, res.status_code)

    
def on_delete_by_name(self, cmd_name, cmd_info, id_LD):
    try:
        if "cmd-qos" in cmd_info and int(cmd_info['cmd-qos']) == 2:
            self.publish_actuation_commandResult_message(cmd_name, cmd_info, id_LD, "Error: cmd-qos must be 0 or 1.")
            return
        
        # get the name of the person to delete
        nuri=get_silo_name(cmd_info['cmd-nuri'])
        name=nuri+"_"+cmd_info['cmd-value']['name']

        # check if this name is registered
        if name not in image_count:
            if "cmd-qos" in cmd_info:
                if int(cmd_info['cmd-qos']) > 0:
                    self.publish_actuation_commandResult_message(cmd_name, cmd_info, id_LD, "The name "+name+" doesn't exist.")
            return
        
        # send to the camera system the deletion request
        _camera_ip, _camera_port=get_camera_ip_port()
        res=requests.delete("http://"+_camera_ip+':'+_camera_port+'/people/'+name)

        # check response
        if res.status_code>=400:
            if "cmd-qos" in cmd_info:
                if int(cmd_info['cmd-qos']) > 0:
                    self.publish_actuation_commandResult_message(cmd_name, cmd_info, id_LD, res.status_code)
            return

        # find all ids of images to delete
        temp=[]
        for x in image_to_name_mapping:
            if image_to_name_mapping[x]==name:
                temp.append(x)
        
        # delete images
        with app.app_context():
            with app.test_request_context():
                for x in temp:
                    #deleteitem_internal('faceInput', {"_id": x})
                    del image_to_name_mapping[x]
        del image_count[name]

        print("")
        print("Deleted person "+name)
        print("Current status:")
        print(image_to_name_mapping)
        print(image_count)
        print("")

        if "cmd-qos" in cmd_info:
            if int(cmd_info['cmd-qos']) > 0:
                self.publish_actuation_commandResult_message(cmd_name, cmd_info, id_LD, "OK")
    except:
        traceback.print_exc()


def initialize_vthing(vthingindex, type, description, commands):
    v_things[vthingindex]={}

    v_things[vthingindex]['name']=vthingindex
    v_things[vthingindex]['type_attr']=type
    v_things[vthingindex]['ID']=thing_visor_ID + "/" + n
    v_things[vthingindex]['label']=vthingindex
    v_things[vthingindex]['description']=description
    v_things[vthingindex]['v_thing']={
        "label": v_things[vthingindex]['label'],
        "id": v_things[vthingindex]['ID'],
        "description": v_things[vthingindex]['description']
    }
    v_things[vthingindex]['caching']=False

    v_things[vthingindex]['ID_LD']="urn:ngsi-ld:"+thing_visor_ID+":" + v_things[vthingindex]['name']

    # Context is a "map" of current virtual thing state
    # create and save the Context for the new vThing
    v_things[vthingindex]['context']=Context()

    # set topic the name of mqtt topic on witch publish vThing data
    # e.g vThing/helloWorld/hello
    v_things[vthingindex]['topic']=v_thing_prefix + "/" + v_things[vthingindex]['ID']

    # set the commands array for the vThing
    v_things[vthingindex]['commands']=commands

    create_vthing_initial_context(vthingindex)

    # data
    subscribe_vthing_data_in_topic(vthingindex)
    # control
    publish_create_vthing_command(vthingindex)
    subscribe_vthing_control_in_topic(vthingindex)
    return vthingindex


def subscribe_TV_control_topic(client, userdata, flags, rc):
    print("connecting mqtt control")
    # Add message callbacks that will only trigger on a specific subscription match
    client.message_callback_add(tv_control_prefix + "/" + thing_visor_ID + "/" + in_control_suffix, callback_for_mqtt_control_in_TV)
    client.subscribe(tv_control_prefix + "/" + thing_visor_ID + "/" + in_control_suffix)
    print("MQTT control client connected with result code "+str(rc))


def mqtt_control_reconnect(client, userdata, rc):
    if rc != 0:
        print("Unexpected MQTT control channel disconnection.")
    else:
        print("MQTT control channel disconnection.")
    client.reconnect()
    
    
def create_vthing_initial_context(vthingindex):
    print("Creating initial vthing context (commands, initial data...)")
    ngsiLdEntity = { "id" : v_things[vthingindex]['ID_LD'],
                "type" : v_things[vthingindex]['type_attr'],
                "commands" : {"type": "Property", "value": v_things[vthingindex]['commands']},
                "@context" : [ "https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld" ]
                }
    data = [ngsiLdEntity]
    v_things[vthingindex]['context'].set_all(data)
    

def subscribe_vthing_data_in_topic(vthingindex):
    # Subscribe mqtt_data_client to the vThing topic
    mqtt_data_client.message_callback_add(v_things[vthingindex]['topic'] + "/" + in_data_suffix, callback_for_mqtt_data_in_vthing)
    mqtt_data_client.subscribe(v_things[vthingindex]['topic'] + "/" + in_data_suffix)
    
    
def publish_create_vthing_command(vthingindex):
    # Publish on the thingVisor out_control topic the createVThing command and other parameters
    message = { "command" : "createVThing",
                        "thingVisorID" : thing_visor_ID,
                        "vThing" : v_things[vthingindex]['v_thing']
                    }
    mqtt_control_client.publish(tv_control_prefix + "/" + thing_visor_ID + "/" + out_control_suffix, json.dumps(message))


def subscribe_vthing_control_in_topic(vthingindex):
    mqtt_control_client.message_callback_add(v_things[vthingindex]['topic'] + "/" + in_control_suffix, callback_for_mqtt_control_in_vthing)
    mqtt_control_client.subscribe(v_things[vthingindex]['topic'] + '/' + in_control_suffix)


def remove_vthing(vthingindex):
    mqtt_control_thread.publish_deleteVThing_command(vthingindex)
    del v_things[vthingindex]


def get_vthing_name(name):
    name=name.split(':')[-1]
    return name


def get_silo_name(nuri):
    return nuri.split('/')[-2]


def publish_message(message, out_topic):
    msg=json.dumps(message)
    #msg = str(message).replace("\'", "\"")
    print("Message sent on "+out_topic + "\n" + msg+"\n")
    # publish data to out_topic
    mqtt_data_client.publish(out_topic, msg)


def send_message(message, vthingindex):
    # use this function to send into viriot's MQTT
    print("topic name: " + v_things[vthingindex]['topic'] + '/' + v_thing_data_suffix + ", message: " + json.dumps(message))
    # publish received data to data topic by using neutral format
    mqtt_data_client.publish(v_things[vthingindex]['topic'] + '/' + v_thing_data_suffix, json.dumps(message))


def message_to_jres(message):
    # Utility function
    payload = message.payload.decode("utf-8", "ignore")
    print("Received on topic " + message.topic + ": " + str(payload))
    jres = json.loads(payload.replace("\'", "\""))
    return jres
    
    
def callback_for_mqtt_data_in_vthing(mosq, obj, message):
    executor.submit(processor_for_mqtt_data_in_vthing, message)
def processor_for_mqtt_data_in_vthing(message):
    jres = message_to_jres(message)
    try:
        data = jres["data"]
        for entity in data:
            id_LD = entity["id"]
            #if id_LD != ID_LD[-1]:
            #    print("Entity not handled by the Thingvisor, message dropped")
            #    continue
            vthingindex=get_vthing_name(id_LD)
            for cmd in v_things[vthingindex]['commands']:
                if cmd in entity:
                    self.process_actuation_commandRequest(entity)
                    continue
    except:
        traceback.print_exc()


def callback_for_mqtt_control_in_vthing(mosq, obj, message):
    executor.submit(processor_for_mqtt_control_in_vthing, message)
def processor_for_mqtt_control_in_vthing(message):
    jres = message_to_jres(message)
    try:
        command_type = jres["command"]
        name=jres["vThingID"].split('/')[-1]
        n=get_vthing_name(name)
        if command_type == "getContextRequest":
            publish_getContextResponse_command(jres,n)
    except:
        traceback.print_exc()


def callback_for_mqtt_control_in_TV(mosq, obj, message):
    executor.submit(processor_for_mqtt_control_in_TV, message)
def processor_for_mqtt_control_in_TV(message):
    jres = message_to_jres(message)
    try:
        command_type = jres["command"]
        if command_type == "destroyTV":
            destroy_thing_visor(jres)
        elif command_type == "updateTV":
            update_thing_visor(jres)
    except:
        traceback.print_exc()
    return 'invalid command'


def publish_actuation_commandResult_message(cmd_name, cmd_info, id_LD, result_code):
    try:  
        n=get_vthing_name(id_LD)

        pname = cmd_name+"-result"
        pvalue = cmd_info.copy()
        pvalue['cmd-result'] = result_code
        ngsiLdEntityResult = {"id": id_LD,
                                "type": v_things[n]['type_attr'],
                                pname: {"type": "Property", "value": pvalue},
                                "@context": [ "https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld" ]
                                }
        data = [ngsiLdEntityResult]
        # LampActuatorContext.update(data)
        
        message = {"data": data, "meta": {
            "vThingID": v_things[n]['ID']}}  # neutral-format message
        if "cmd-nuri" in cmd_info:
            if cmd_info['cmd-nuri'].startswith("viriot://"):
                topic = cmd_info['cmd-nuri'][len("viriot://"):]
                publish_message(message, topic)
            else:
                publish_message(message, v_things[n]['topic'])
        else:
            publish_message(message, v_things[n]['topic'])
    except:
        traceback.print_exc()


def publish_actuation_commandStatus_message(cmd_name, cmd_info, id_LD, status_code):
    try:  
        n=get_vthing_name(id_LD)

        pname = cmd_name+"-status"
        pvalue = cmd_info.copy()
        pvalue['cmd-status'] = status_code
        ngsiLdEntityStatus = {"id": id_LD,
                                "type": v_things[n]['type_attr'],
                                pname: {"type": "Property", "value": pvalue},
                                "@context": [ "https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld" ]
                                }
        data = [ngsiLdEntityStatus]
        
        message = {"data": data, "meta": {
            "vThingID": v_things[n]['ID']}}  # neutral-format message
        if "cmd-nuri" in cmd_info:
            if cmd_info['cmd-nuri'].startswith("viriot://"):
                topic = cmd_info['cmd-nuri'][len("viriot://"):]
                publish_message(message, topic)
            else:
                publish_message(message, v_things[n]['topic'])
        else:
            publish_message(message, v_things[n]['topic'])
    except:
        traceback.print_exc()


def process_actuation_commandRequest(cmd_entity):
    try:
        #jsonschema.validate(data, commandRequestSchema)
        id_LD = cmd_entity["id"]
        n=get_vthing_name(id_LD)
        for cmd_name in v_things[n]['commands']:
            if cmd_name in cmd_entity:
                cmd_info = cmd_entity[cmd_name]['value']
                fname = cmd_name.replace('-','_')
                fname = "on_"+fname
                f=getattr(self,fname)
                if "cmd-qos" in cmd_info:
                    if int(cmd_info['cmd-qos']) == 2:
                        self.publish_actuation_commandStatus_message(cmd_name, cmd_info, id_LD, "PENDING")
                future = executor.submit(f, cmd_name, cmd_info, id_LD)
    except:
        traceback.print_exc()


def publish_getContextResponse_command(jres, vthingindex):
    silo_id = jres["vSiloID"]
    message = {"command": "getContextResponse", "data": v_things[n]['context'].get_all(), "meta": {"vThingID": v_things[n]['ID']}}
    mqtt_control_client.publish(v_silo_prefix + "/" + silo_id + "/" + in_control_suffix, json.dumps(message))


def publish_deleteVThing_command(vthingindex):
    msg = {"command": "deleteVThing", "vThingID": v_things[n]['ID'], "vSiloID": "ALL"}
    mqtt_control_client.publish(v_thing_prefix + "/" + v_things[n]['ID'] + "/" + out_control_suffix, json.dumps(msg))


def publish_destroyTVAck_command():
    msg = {"command": "destroyTVAck", "thingVisorID": thing_visor_ID}
    mqtt_control_client.publish(tv_control_prefix + "/" + thing_visor_ID + "/" + out_control_suffix, json.dumps(msg))


def destroy_thing_visor(jres):
    db_client.close()
    for n in v_things:
        publish_deleteVThing_command(n)
    publish_destroyTVAck_command()
    print("Shutdown completed")


def update_thing_visor(jres):
    global fps
    print("Print update_info:", jres['update_info'])
    if 'fps' in jres['params']:
        fps=jres['params']['fps']


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

    port_mapping = db[thing_visor_collection].find_one({"thingVisorID": thing_visor_ID}, {"port": 1, "_id": 0})
    print("port mapping: " + str(port_mapping))

    # mqtt settings
    tv_control_prefix = "TV"  # prefix name for controller communication topic
    v_thing_prefix = "vThing"  # prefix name for virtual Thing data and control topics
    v_thing_data_suffix = "data_out"
    in_control_suffix = "c_in"
    out_control_suffix = "c_out"
    out_data_suffix = "data_out"
    in_data_suffix = "data_in"
    v_silo_prefix = "vSilo"

    mqtt_control_client = mqtt.Client()
    mqtt_control_client.on_connect = subscribe_TV_control_topic
    mqtt_control_client.on_disconnect = mqtt_control_reconnect
    mqtt_control_client.connect(MQTT_control_broker_IP, MQTT_control_broker_port, 30)
    mqtt_data_client = mqtt.Client()
    mqtt_data_client.connect(MQTT_data_broker_IP, MQTT_data_broker_port, 30)
    # starting the two threads, each for each mqtt client we have
    print("Entering main MQTT network loop")
    mqtt_data_client.loop_start()
    mqtt_control_client.loop_start()
    
    # threadPoolExecutor of default size
    executor = ThreadPoolExecutor()    


    # CUSTOM TO THIS THINGVISOR
    fps=None
    upstream_camera_sensor=None

    if params:
        if 'upstream_camera_sensor' in params:
            upstream_camera_sensor = params['upstream_camera_sensor']
        if 'fps' in params:
            fps = params['fps']

    # Map images to names
    image_to_name_mapping={}
    # store image count for every name
    image_count={}


    # FOR ACTUATION
    # for each command we receive, store the command information BL BLA
    # NOTE that the native dict type is inherently thread safe in python, so
    # the two threads can concurrently modify it. Moreover, the dict is global
    # because variables in python have global visibility, unless when you CHANGE
    # it, in that case a NEW, LOCAL variable is created if you don't use the global keyword.
    command_data={}
    v_things={}

    # create the detector vThing: name, type, description, array of commands
    detector=initialize_vthing("detector","FaceDetector","faceRecognition virtual thing",["start","stop","set-face-feature","delete-by-name"])

    # set eve callbacks
    app.on_post_PATCH_faceInput += on_post_PATCH_faceInput
    app.on_post_POST_faceOutput += on_post_POST_faceOutput

    # runs eve, and ends the main thread
    app.run(debug=False,host='0.0.0.0',port='5000')
