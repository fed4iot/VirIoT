#! /usr/local/bin/python3

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

# Fed4IoT ThingVisor hello world actuator

import time
import os
import random
import json
import traceback
import string
import paho.mqtt.client as mqtt
import jsonschema
from threading import Thread
from pymongo import MongoClient
from context import Context
from phue import Bridge

from concurrent.futures import ThreadPoolExecutor

# -*- coding: utf-8 -*-


class DataThread(Thread):
    # Class used to:
    # 1) handle actuation command workflow
    # 2) publish actuator status when it changes
    global mqtt_data_client, LampActuatorContext, executor, commands
 
    def send_commandResult(self, cmd_name, cmd_info, id_LD, result_code):
        global v_things
        pname = cmd_name+"-result"
        pvalue = cmd_info.copy()
        pvalue['cmd-result'] = result_code
        ngsiLdEntityResult = {"id": id_LD,
                              "type": v_things[id_LD]['ld_type'],
                              pname: {"type": "Property", "value": pvalue}
                              }
        data = [ngsiLdEntityResult]
        
        message = {"data": data, "meta": {
            "vThingID": v_things[id_LD]['vThing']['id']}}  # neutral-format message
        if "cmd-nuri" in cmd_info:
            if cmd_info['cmd-nuri'].startswith("viriot://"):
                topic = cmd_info['cmd-nuri'][len("viriot://"):]
            else:
                topic = v_things[id_LD]['topic']+"/"+data_out_suffix
        else:
            topic = v_things[id_LD]['topic']+"/"+data_out_suffix
        publish(mqtt_data_client,message,topic)

    def send_commandStatus(self, cmd_name, cmd_info, id_LD, status_code):
        global v_things
        pname = cmd_name+"-status"
        pvalue = cmd_info.copy()
        pvalue['cmd-status'] = status_code
        ngsiLdEntityResult = {"id": id_LD,
                              "type": v_things[id_LD]['ld_type'],
                              pname: {"type": "Property", "value": pvalue}
                              }
        data = [ngsiLdEntityResult]
        
        message = {"data": data, "meta": {
            "vThingID": v_things[id_LD]['vThing']['id']}}  # neutral-format message
        if "cmd-nuri" in cmd_info:
            if cmd_info['cmd-nuri'].startswith("viriot://"):
                topic = cmd_info['cmd-nuri'][len("viriot://"):]
            else:
                topic = v_things[id_LD]['topic']+"/"+data_out_suffix
        else:
            topic = v_things[id_LD]['topic']+"/"+data_out_suffix
        publish(mqtt_data_client,message,topic)

    def receive_commandRequest(self, cmd_entity):
        try:
            #jsonschema.validate(data, commandRequestSchema)
            id_LD = cmd_entity["id"]
            for cmd_name in commands:
                if cmd_name in cmd_entity:
                    cmd_info = cmd_entity[cmd_name]['value']
                    fname = cmd_name.replace('-', '_')
                    fname = "on_"+fname
                    f = getattr(self, fname)
                    if "cmd-qos" in cmd_info:
                        if int(cmd_info['cmd-qos']) == 2:
                            self.send_commandStatus(
                                cmd_name, cmd_info, id_LD, "PENDING")
                    future = executor.submit(
                        f, cmd_name, cmd_info, id_LD, self)

        # except jsonschema.exceptions.ValidationError as e:
            #print("received commandRequest got a schema validation error: ", e)
        # except jsonschema.exceptions.SchemaError as e:
            #print("commandRequest schema not valid:", e)
        except Exception as ex:
            traceback.print_exc()
        return
    
    def on_raw_command(self, cmd_name, cmd_info, id_LD, actuatorThread):
        global contexts, lights, pbridge
        # function to change the color of the Lamp should be written here
        # update the Context, publish new actuator status on data_out, send result
        try:
            context = contexts[id_LD]
            light_id = v_things[id_LD]['light_id']
            light = lights[light_id]
            pbridge.set_light(light_id,cmd_info['cmd-value'])

            # reload status
            ngsiLdEntity = {"id": id_LD,
                "type": v_things[id_LD]['ld_type'],
                "brightness": {"type": "Property", "value": light.brightness},
                "saturation": {"type": "Property", "value": light.saturation},
                "hue": {"type": "Property", "value": light.hue},
                "on": {"type": "Property", "value": light.on},
                "commands": {"type": "Property", "value": commands}
                }

            data = [ngsiLdEntity]
            context.update(data)

            # publish changed status
            message = {"data": data, "meta": {
                "vThingID": v_things[id_LD]['vThing']['id']}}  # neutral-format
            publish(mqtt_data_client, message,v_things[id_LD]['topic']+"/"+data_out_suffix)
            cmd_result = "OK"
        except Exception as ex:
            cmd_result = "FAIL"

        # publish command result
        if "cmd-qos" in cmd_info:
            if int(cmd_info['cmd-qos']) > 0:
                self.send_commandResult(cmd_name, cmd_info, id_LD, cmd_result)

    def on_set_value(self, cmd_name, cmd_info, id_LD, actuatorThread):
        global contexts, lights
        # function to change the color of the Lamp should be written here
        # update the Context, publish new actuator status on data_out, send result
        try:
            context = contexts[id_LD]
            light_id = v_things[id_LD]['light_id']
            param = cmd_name.split("-")[1]
            light = lights[light_id]
            if param == "brightness":
                light.brightness = cmd_info['cmd-value']
            elif param == "saturation":
                light.saturation = cmd_info['cmd-value']
            elif param == "hue":
                light.hue = cmd_info['cmd-value']
            elif param == "on":
                light.on = cmd_info['cmd-value']
            else:
                cmd_result = "FAIL"
                return

            ngsiLdEntity = {"id": id_LD,
                            "type": v_things[id_LD]['ld_type'],
                            #param: {"type": "Property", "value": cmd_info['cmd-value']}
                            param: {"type": "Property", "value": eval("light."+param)}
                            }
            
            data = [ngsiLdEntity]
            context.update(data)

            # publish changed status
            message = {"data": data, "meta": {
                "vThingID": v_things[id_LD]['vThing']['id']}}  # neutral-format
            publish(mqtt_data_client, message,v_things[id_LD]['topic']+"/"+data_out_suffix)
            cmd_result = "OK"
        except Exception as ex:
            cmd_result = "FAIL"

        # publish command result
        if "cmd-qos" in cmd_info:
            if int(cmd_info['cmd-qos']) > 0:
                self.send_commandResult(cmd_name, cmd_info, id_LD, cmd_result)



    def on_message_data_in_vThing(self, mosq, obj, msg):
        global v_things, commands
        payload = msg.payload.decode("utf-8", "ignore")
        print("Message received on "+msg.topic + "\n" + payload+"\n")
        try:
            # jres = json.loads(payload.replace("\'", "\""))
            jres = json.loads(payload)
            data = jres["data"]
            for entity in data:
                id_LD = entity["id"]
                if id_LD not in v_things.keys():
                    print("Entity not handled by the Thingvisor, message dropped")
                    continue
                for cmd in commands:
                    if cmd in entity:
                        self.receive_commandRequest(entity)
                        continue
            return
        except Exception as ex:
            traceback.print_exc()
        return

    def __init__(self):
        Thread.__init__(self)
        self.on_set_brightness = self.on_set_value
        self.on_set_saturation = self.on_set_value
        self.on_set_hue = self.on_set_value
        self.on_set_on = self.on_set_value

    def run(self):
        global commands, lights, contexts, vthings

        mqtt_data_client.connect(
            MQTT_data_broker_IP, MQTT_data_broker_port, 30)
        print("Thread mqtt data started")

        commands = ["set-brightness", "set-saturation", "set-hue",
                    "set-on", "raw-command"]

        # Create initial context and data subscriptions
        # v_things[id_LD] = {"vThing": {"label": label, "id": v_thing_ID, "description": description, "type": "actuator"},"light_id":light.light_id}
        for v_thing_ID_LD in v_things:
            v_thing_ID = v_things[v_thing_ID_LD]['vThing']['id']
            light_id = v_things[v_thing_ID_LD]['light_id']
            v_thing_type_attr = v_things[v_thing_ID_LD]['ld_type']
            v_thing_data_in_topic = v_thing_prefix + \
                "/" + v_thing_ID + "/" + data_in_suffix
            light = lights[light_id]
            ngsiLdEntity = {"id": v_thing_ID_LD,
                            "type": v_thing_type_attr,
                            "brightness": {"type": "Property", "value": light.brightness},
                            "saturation": {"type": "Property", "value": light.saturation},
                            "hue": {"type": "Property", "value": light.hue},
                            "on": {"type": "Property", "value": light.on},
                            "commands": {"type": "Property", "value": commands}
                            }

            data = [ngsiLdEntity]
            contexts[v_thing_ID_LD] = Context()
            contexts[v_thing_ID_LD].set_all(data)

            # define callback and subscriptions for data_in where to receive actuator commands
            mqtt_data_client.message_callback_add(v_thing_data_in_topic,
                                                  self.on_message_data_in_vThing)
            mqtt_data_client.subscribe(v_thing_data_in_topic)

        mqtt_data_client.loop_forever()
        print("Thread '" + self.name + "' terminated")


class ControlThread(Thread):

    def on_message_get_thing_context(self, jres):
        silo_id = jres["vSiloID"]
        v_thing_id = jres["vThingID"]
        id_LD = "urn:ngsi-ld:"+v_thing_id.replace("/",":")
        msg = {"command": "getContextResponse", "data": contexts[id_LD].get_all(), "meta": {"vThingID": v_thing_id}}
        publish(mqtt_control_client, msg, v_silo_prefix + "/" + silo_id + "/" + control_in_suffix)

    def send_destroy_v_thing_message(self):
        for v_thing_ID_LD in v_things:
            v_thing_ID = v_things[v_thing_ID_LD]["vThing"]["id"]
            msg = {"command": "deleteVThing", "vThingID": v_thing_ID, "vSiloID": "ALL"}
            publish(mqtt_control_client, msg, v_thing_prefix + "/" + v_thing_ID + "/" + control_out_suffix)
        return

    def send_destroy_thing_visor_ack_message(self):
        msg = {"command": "destroyTVAck", "thingVisorID": thing_visor_ID}
        publish(mqtt_control_client, msg, tv_prefix + "/" + thing_visor_ID + "/" + control_out_suffix)
        return

    def on_message_destroy_thing_visor(self, jres):
        global db_client
        db_client.close()
        self.send_destroy_v_thing_message()
        self.send_destroy_thing_visor_ack_message()
        print("Shutdown completed")

    def on_message_control_in_vThing(self, mosq, obj, msg):
        payload = msg.payload.decode("utf-8", "ignore")
        print(msg.topic + " " + str(payload)+"\n")
        # jres = json.loads(payload.replace("\'", "\""))
        jres = json.loads(payload)
        try:
            command_type = jres["command"]
            if command_type == "getContextRequest":
                self.on_message_get_thing_context(jres)
        except Exception as ex:
            traceback.print_exc()
        return

    def on_message_control_in_TV(self, mosq, obj, msg):
        payload = msg.payload.decode("utf-8", "ignore")
        print(msg.topic + " " + str(payload)+"\n")
        # jres = json.loads(payload.replace("\'", "\""))
        jres = json.loads(payload)
        try:
            command_type = jres["command"]
            if command_type == "destroyTV":
                self.on_message_destroy_thing_visor(jres)
        except Exception as ex:
            traceback.print_exc()
        return 'invalid command'

        # handler for mqtt control topics

    def __init__(self):
        Thread.__init__(self)

    def run(self):
        print("Thread mqtt control started")
        global mqtt_control_client
        mqtt_control_client.connect(
            MQTT_control_broker_IP, MQTT_control_broker_port, 30)

        # Publish on the thingVisor out_control topic the createVThing command and other parameters for each vThing
        for v_thing_ID_LD in v_things:
            v_thing_topic = v_things[v_thing_ID_LD]["topic"]
            v_thing_message = {"command": "createVThing",
                               "thingVisorID": thing_visor_ID,
                               "vThing":  v_things[v_thing_ID_LD]["vThing"]}
            publish(mqtt_control_client, v_thing_message, tv_prefix + "/" + thing_visor_ID + "/" + control_out_suffix)

            # Add message callbacks that will only trigger on a specific subscription match
            mqtt_control_client.message_callback_add(v_thing_topic + "/" + control_in_suffix,
                                                     self.on_message_control_in_vThing)
            mqtt_control_client.message_callback_add(tv_prefix + "/" + thing_visor_ID + "/" + control_in_suffix,
                                                     self.on_message_control_in_TV)
            mqtt_control_client.subscribe(
                v_thing_topic + '/' + control_in_suffix)
            mqtt_control_client.subscribe(
                tv_prefix + "/" + thing_visor_ID + "/" + control_in_suffix)
            time.sleep(0.1)
        mqtt_control_client.loop_forever()
        print("Thread '" + self.name + "' terminated")


def randomString(stringLength=10):
    """Generate a random string of fixed length """
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(stringLength))


def initHue():
    global pbridge, v_things, lights, contexts
    # Connection with Hue Bridge
    while True:
        try:
            pbridge = Bridge(bridgeIP+":"+bridgePort, config_file_path=".huecfg")
            break
        except Exception as ex:
            print(ex)
            time.sleep(5)
            continue
    # If the app is not registered and the button is not pressed, press the button and call connect() (this only needs to be run a single time)
    i = 1
    while True: 
        print("Connection attempt with Hue bridge n."+str(i))
        try:
            print("Hue bridge connection attempt..."+str(i))
            pbridge.connect()
            if pbridge.username == None:
                time.sleep(5)
                i += 1
                continue
            print("Hue bridge connected...")
            break
        except Exception as ex:
            print(ex)
            time.sleep(5)
            i += 1
            continue

    # Get connected lights and builds
    lights = pbridge.get_light_objects('id')
    v_things = dict()
    for light_id in lights:
        tid = "light"+str(light_id)
        light = lights[light_id]
        v_thing_ID = thing_visor_ID + "/" + tid
        description = light.type
        label = light.name
        id_LD = "urn:ngsi-ld:"+v_thing_ID.replace("/", ":")
        v_things[id_LD] = {"vThing": {"label": label, "id": v_thing_ID,
                                      "description": description, "type": "actuator"}, 
                                      "light_id": light_id, "ld_type": description,
                                      "topic": v_thing_prefix+"/"+v_thing_ID}

def publish(mqtt_client, message, out_topic):
    # msg = str(message).replace("\'", "\"")
    msg = json.dumps(message)
    print("Message sent on "+out_topic + "\n" + msg+"\n")
    # publish data to out_topic
    mqtt_data_client.publish(out_topic, msg)

# main
if __name__ == '__main__':
    # v_thing_ID = os.environ["vThingID_0"]
    thing_visor_ID = os.environ["thingVisorID"]

    MQTT_data_broker_IP = os.environ["MQTTDataBrokerIP"]
    MQTT_data_broker_port = int(os.environ["MQTTDataBrokerPort"])
    MQTT_control_broker_IP = os.environ["MQTTControlBrokerIP"]
    MQTT_control_broker_port = int(os.environ["MQTTControlBrokerPort"])

    tv_prefix = "TV"  # prefix name for controller communication topic
    v_thing_prefix = "vThing"  # prefix name for virtual Thing data and control topics
    data_out_suffix = "data_out"
    data_in_suffix = "data_in"
    control_in_suffix = "c_in"
    control_out_suffix = "c_out"
    v_silo_prefix = "vSilo"

    # import paramenters from environments
    # parameters = str(os.environ.get("params")).replace("'", '"')
    parameters = os.environ.get("params")
    params=[]
    if parameters:
        try:
            params = json.loads(parameters)
        except json.decoder.JSONDecodeError:
            # TODO manage exception
            print("error on params (JSON) decoding"+"\n")
    if "bridgeIP" not in params:
        bridgeIP = "172.17.0.1"
    else:
        bridgeIP = params["bridgeIP"]
    if "bridgePort" not in params:
        bridgePort = "8000"
    else:
        bridgePort = params["bridgePort"]

    # initialize Hue bridge connection and creates pbridge global variable, and the v_things and lights global collections
    contexts = dict()
    lights = dict()
    v_things = dict()
    initHue()

    # Mongodb settings
    time.sleep(1.5)  # wait before query the system database
    db_name = "viriotDB"  # name of system database
    thing_visor_collection = "thingVisorC"
    db_IP = os.environ['systemDatabaseIP']  # IP address of system database
    db_port = os.environ['systemDatabasePort']  # port of system database
    db_client = MongoClient('mongodb://' + db_IP + ':' + str(db_port) + '/')
    db = db_client[db_name]
    port_mapping = db[thing_visor_collection].find_one(
        {"thingVisorID": thing_visor_ID}, {"port": 1, "_id": 0})
    print("port mapping: " + str(port_mapping)+"\n")

    mqtt_control_client = mqtt.Client()
    mqtt_data_client = mqtt.Client()

    # threadPoolExecutor of size one to handle one command at a time in a fifo order
    executor = ThreadPoolExecutor(1)

    # Class used to handle data and commands of the actuator
    data_thread = DataThread()
    data_thread.start()

    control_thread = ControlThread()  # mqtt control thread
    control_thread.start()

    while True:
        try:
            time.sleep(3)
        except:
            print("KeyboardInterrupt"+"\n")
            time.sleep(1)
            os._exit(1)
