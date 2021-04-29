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
import uuid

from eve import Eve
from flask import request, Response

from eve.io.base import BaseJSONEncoder
from eve.io.mongo import Validator
from eve.methods.post import post_internal
from eve.methods.delete import deleteitem_internal

import master_controller_invoke_REST as rest


# validator for custom uuid type
# in this case, it's an integer that must not be negative
class UUIDValidator(Validator):
    """
    Extends the base mongo validator adding support for the uuid data-type
    """
    def _validate_type_uuid(self, value):
        if isinstance(value,int):
            if value>=0:
                return True

# initialize Eve
app = Eve(validator=UUIDValidator)


# function for sending messages through mqtt
def send_message(message, n):
    print("topic name: " + v_things[n]['topic'] + '/' + v_thing_data_suffix + ", message: " + json.dumps(message))
    mqtt_data_client.publish(v_things[n]['topic'] + '/' + v_thing_data_suffix,
                                json.dumps(message))  # publish received data to data topic by using neutral format

def create_vthing(n, type, commands):
    v_things[n]={}

    v_things[n]['name']=n
    v_things[n]['type_attr']=type
    v_things[n]['ID']=thing_visor_ID + "/" + n
    v_things[n]['label']=n
    v_things[n]['description']="generic virtual thing"
    v_things[n]['v_thing']={
        "label": v_things[n]['label'],
        "id": v_things[n]['ID'],
        "description": v_things[n]['description']
    }

    v_things[n]['ID_LD']="urn:ngsi-ld:"+thing_visor_ID+":" + v_things[n]['name']

    # create and save the Context for the new vThing
    # Context is a "map" of current virtual thing state
    v_things[n]['context']=Context()

    # set topic the name of mqtt topic on witch publish vThing data
    # e.g. vThing/helloWorld/hello
    v_things[n]['topic']=v_thing_prefix + "/" + v_things[n]['ID']

    # set the commands array for the vThing
    v_things[n]['commands']=commands

    # control thread
    mqtt_control_thread.create_vthing(n)

    # data thread
    mqtt_data_thread.create_vthing(n)

    return n

def destroy_vthing(n):
    mqtt_control_thread.send_destroy_v_thing_message(n)
    delete_endpoint(n)
    del v_things[n]

# create vthing endpoint through REST
def create_endpoint(n):
    time.sleep(6)
    print("Creating endpoint for "+n)
    rest.set_vthing_endpoint(controller_url, v_things[n]['ID'], "http://localhost:5000", tenant_id, admin_psw)

# delete vthing endpoint through REST
def delete_endpoint(n):
    print("Destroying endpoint for "+n)
    rest.del_vthing_endpoint(controller_url, v_things[n]['ID'], tenant_id, admin_psw)

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
            n=get_vthing_name(id_LD)

            pname = cmd_name+"-result"
            pvalue = cmd_info.copy()
            pvalue['cmd-result'] = payload
            ngsiLdEntityResult = {"id": id_LD,
                                    "type": v_things[n]['type_attr'],
                                    pname: {"type": "Property", "value": pvalue},
                                    "@context": [ "https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld" ]
                                    }
            data = [ngsiLdEntityResult]
            message = {"data": data, "meta": {
                "vThingID": v_things[n]['ID']
            }}  # neutral-format message

            if "cmd-nuri" in cmd_info:
                if cmd_info['cmd-nuri'].startswith("viriot://"):
                    topic = cmd_info['cmd-nuri'][len("viriot://"):]
                    self.publish(message, topic)
                else:
                    self.publish(message, v_things[n]['topic'])
            else:
                self.publish(message, v_things[n]['topic'])
        except:
            traceback.print_exc()

    def send_commandStatus(self, cmd_name, cmd_info, id_LD, status_code):
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
                "vThingID": v_things[n]['ID']
            }}  # neutral-format message
            
            if "cmd-nuri" in cmd_info:
                if cmd_info['cmd-nuri'].startswith("viriot://"):
                    topic = cmd_info['cmd-nuri'][len("viriot://"):]
                    self.publish(message, topic)
                else:
                    self.publish(message, v_things[n]['topic'])
            else:
                self.publish(message, v_things[n]['topic'])
        except:
            traceback.print_exc()

    def receive_commandRequest(self, cmd_entity):
        try:
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
                n=get_vthing_name(id_LD)
                for cmd in v_things[n]['commands']:
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
        mqtt_data_client.loop_forever()
        print("Thread '" + self.name + "' terminated")

    def create_vthing(self,n):
        ngsiLdEntity = {"id": v_things[n]['ID_LD'],
            "type": v_things[n]['type_attr'],
            "commands": {"type": "Property", "value": v_things[n]['commands']},
            "@context": [ "https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld" ]
        }
        data = [ngsiLdEntity]
        v_things[n]['context'].set_all(data)

        mqtt_data_client.message_callback_add(v_things[n]['topic'] + "/" + in_data_suffix,
                                            self.on_message_data_in_vThing)
        # Subscribe mqtt_data_client to the vThing topic
        mqtt_data_client.subscribe(
            v_things[n]['topic'] + "/" + in_data_suffix)


class MqttControlThread(Thread):
    def on_message_get_thing_context(self, jres,n):
        silo_id = jres["vSiloID"]
        message = {"command": "getContextResponse", "data": v_things[n]['context'].get_all(), "meta": {"vThingID": v_things[n]['ID']}}
        mqtt_control_client.publish(v_silo_prefix + "/" + silo_id + "/" + in_control_suffix, json.dumps(message))

    def send_destroy_v_thing_message(self,n):
        msg = {"command": "deleteVThing", "vThingID": v_things[n]['ID'], "vSiloID": "ALL"}
        mqtt_control_client.publish(v_thing_prefix + "/" + v_things[n]['ID'] + "/" + out_control_suffix, json.dumps(msg))

    def send_destroy_thing_visor_ack_message(self):
        msg = {"command": "destroyTVAck", "thingVisorID": thing_visor_ID}
        mqtt_control_client.publish(tv_control_prefix + "/" + thing_visor_ID + "/" + out_control_suffix, json.dumps(msg))

    def on_message_destroy_thing_visor(self, jres):
        global db_client
        db_client.close()
        for n in v_things:
            self.send_destroy_v_thing_message(n)
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
            name=jres["vThingID"].split('/')[-1]
            n=get_vthing_name(name)
            if command_type == "getContextRequest":
                self.on_message_get_thing_context(jres,n)
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

        # Add message callbacks that will only trigger on a specific subscription match
        mqtt_control_client.message_callback_add(tv_control_prefix + "/" + thing_visor_ID + "/" + in_control_suffix,
                                                 self.on_message_in_control_TV)
        mqtt_control_client.subscribe(tv_control_prefix + "/" + thing_visor_ID + "/" + in_control_suffix)

        mqtt_control_client.loop_forever()
        print("Thread '" + self.name + "' terminated")
    
    def create_vthing(self,n):
        # Publish on the thingVisor out_control topic the createVThing command and other parameters
        v_thing_message = {"command": "createVThing",
                        "thingVisorID": thing_visor_ID,
                        "vThing": v_things[n]['v_thing']}
        mqtt_control_client.publish(tv_control_prefix + "/" + thing_visor_ID + "/" + out_control_suffix,
                                    json.dumps(v_thing_message))

        # create endpoint
        executor.submit(create_endpoint, n)

        # Add message callbacks that will only trigger on a specific subscription match
        mqtt_control_client.message_callback_add(v_things[n]['topic'] + "/" + in_control_suffix,
                                                self.on_message_in_control_vThing)
        mqtt_control_client.subscribe(v_things[n]['topic'] + '/' + in_control_suffix)

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
    controller_url=None
    tenant_id=None
    admin_psw=None

    if params:
        if 'controller_url' in params:
            controller_url = params['controller_url']
        if 'tenant_id' in params:
            tenant_id = params['tenant_id']
        if 'admin_psw' in params:
            admin_psw = params['admin_psw']

    # create v_things dictionary
    v_things={}

    # mqtt settings
    tv_control_prefix = "TV"  # prefix name for controller communication topic
    v_thing_prefix = "vThing"  # prefix name for virtual Thing data and control topics
    v_thing_data_suffix = "data_out"
    in_control_suffix = "c_in"
    out_control_suffix = "c_out"
    out_data_suffix = "data_out"
    in_data_suffix = "data_in"
    v_silo_prefix = "vSilo"

    port_mapping = db[thing_visor_collection].find_one({"thingVisorID": thing_visor_ID}, {"port": 1, "_id": 0})
    print("port mapping: " + str(port_mapping))

    mqtt_control_client = mqtt.Client()
    mqtt_data_client = mqtt.Client()

    # threadPoolExecutor of size one to handle one command at a time in a fifo order
    executor = ThreadPoolExecutor(1)

    mqtt_control_client.connect(MQTT_control_broker_IP, MQTT_control_broker_port, 30)
    mqtt_control_thread = MqttControlThread()  # mqtt control thread
    mqtt_control_thread.start()

    mqtt_data_client.connect(MQTT_data_broker_IP, MQTT_data_broker_port, 30)
    mqtt_data_thread = mqttDataThread()  # mqtt data thread
    mqtt_data_thread.start()

    # create the sample vThing
    sample=create_vthing("sample","Sample",["GENERIC_COMMAND"])

    # run eve
    app.run(debug=False,host='0.0.0.0',port='5000')

    # # loop until keyboard interrupt
    # while True:
    #     try:
    #         time.sleep(3)
    #     except:
    #         print("KeyboardInterrupt"+"\n")
    #         time.sleep(1)
    #         os._exit(1)
