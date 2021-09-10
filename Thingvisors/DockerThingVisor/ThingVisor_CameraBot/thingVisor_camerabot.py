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

import master_controller_invoke_REST as rest

# -*- coding: utf-8 -*-

# validator for custom uuid type
# in this case, it's an integer representing the camera number
class UUIDValidator(Validator):
    """
    Extends the base mongo validator adding support for the uuid data-type
    """
    def _validate_type_uuid(self, value):
        if isinstance(value,int):
            if value>=0:
                return True

app = Eve(validator=UUIDValidator)

# initialization route
# deletes all the cameras
# then create a number of cameras equal to num_of_cameras constant
@app.route('/init')
def init():
    deleteitem_internal('cameras', {})
    deleteitem_internal('robots', {})
    for i in range(num_of_cameras):
        post_internal('cameras', {"_id": i})
    post_internal('robots', {"_id": 0})
    return "OK"

@app.route('/cameras/<_id>/image')
def get_camera_image(_id):
    global v_thing_caching

    cameras = app.data.driver.db['cameras']
    a = cameras.find_one({'_id':int(_id)})
    b=app.media.get(a['data'])

    headers={"Content-disposition":
                    "attachment; filename=image.png"}

    if not v_thing_caching[int(_id)]:
        headers["Cache-Control"]="no-cache"

    return Response(
        b.read(),
        mimetype="image/png",
        headers=headers)

def send_message(message, i):
    print("topic name: " + v_thing_topic[i] + '/' + v_thing_data_suffix + ", message: " + json.dumps(message))
    mqtt_data_client.publish(v_thing_topic[i] + '/' + v_thing_data_suffix,
                                json.dumps(message))  # publish received data to data topic by using neutral format

def get_vthing_index(name):
    name=name.split(':')[-1]
    if name=="robot":
        return(num_of_cameras)
    return(int(name[6:]))

class mqttDataThread(Thread):
    # Class used to:
    # 1) handle actuation command workflow
    # 2) publish actuator status when it changes
    global mqtt_data_client, context_camera, executor, commands

    def send_commandResult(self, cmd_name, cmd_info, id_LD, result_code):
        pname = cmd_name+"-result"
        pvalue = cmd_info.copy()
        pvalue['cmd-result'] = result_code
        ngsiLdEntityResult = {"id": id_LD,
                                "type": v_thing_type_attr[-1],
                                pname: {"type": "Property", "value": pvalue},
                                "@context": [ "https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld" ]
                                }
        data = [ngsiLdEntityResult]
        # LampActuatorContext.update(data)
        
        message = {"data": data, "meta": {
            "vThingID": v_thing_ID[-1]}}  # neutral-format message
        if "cmd-nuri" in cmd_info:
            if cmd_info['cmd-nuri'].startswith("viriot://"):
                topic = cmd_info['cmd-nuri'][len("viriot://"):]
                self.publish(message, topic)
            else:
                self.publish(message)
        else:
            self.publish(message)

    def send_commandStatus(self, cmd_name, cmd_info, id_LD, status_code):
        pname = cmd_name+"-status"
        pvalue = cmd_info.copy()
        pvalue['cmd-status'] = status_code
        ngsiLdEntityStatus = {"id": id_LD,
                                "type": v_thing_type_attr[-1],
                                pname: {"type": "Property", "value": pvalue},
                                "@context": [ "https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld" ]
                                }
        data = [ngsiLdEntityStatus]
        
        message = {"data": data, "meta": {
            "vThingID": v_thing_ID[-1]}}  # neutral-format message
        if "cmd-nuri" in cmd_info:
            if cmd_info['cmd-nuri'].startswith("viriot://"):
                topic = cmd_info['cmd-nuri'][len("viriot://"):]
                self.publish(message, topic)
            else:
                self.publish(message)
        else:
            self.publish(message)

    def receive_commandRequest(self, cmd_entity):
        try:  
            #jsonschema.validate(data, commandRequestSchema)
            id_LD = cmd_entity["id"]
            i=get_vthing_index(id_LD)
            for cmd_name in commands[i]:
                if cmd_name in cmd_entity:
                    cmd_info = cmd_entity[cmd_name]['value']
                    fname = cmd_name.replace('-','_')
                    fname = "on_"+fname
                    f=getattr(self,fname)
                    if "cmd-qos" in cmd_info:
                        if int(cmd_info['cmd-qos']) == 2:
                            self.send_commandStatus(cmd_name, cmd_info, id_LD, "PENDING")
                    future = executor.submit(f, cmd_name, cmd_info, id_LD, self)
                    

        #except jsonschema.exceptions.ValidationError as e:
            #print("received commandRequest got a schema validation error: ", e)
        #except jsonschema.exceptions.SchemaError as e:
            #print("commandRequest schema not valid:", e)
        except Exception as ex:
            traceback.print_exc()
        return

    def get_robot_ip_port(self):
        global robot_ip,robot_port
        if robot_ip==None or robot_port==None:
            with app.app_context():
                robots = app.data.driver.db['robots']
                a = robots.find_one({'_id':0})
                return a['ip'], a['port']
        else:
            return robot_ip, robot_port

    def on_set_caching(self, cmd_name, cmd_info, id_LD, actuatorThread):
        global v_thing_caching

        i=get_vthing_index(id_LD)

        print("Setting caching for camera"+str(i)+" to "+str(cmd_info['cmd-value']))
        v_thing_caching[i]=cmd_info['cmd-value']

        if "cmd-qos" in cmd_info:
            if int(cmd_info['cmd-qos']) > 0:
                self.send_commandResult(cmd_name, cmd_info, id_LD, "OK")


    def on_start(self, cmd_name, cmd_info, id_LD, actuatorThread):
        print("Sending start command to robot")
        _robot_ip, _robot_port=self.get_robot_ip_port()
        print("ip: "+_robot_ip+"  port: "+_robot_port)
        requests.get("http://"+_robot_ip+':'+_robot_port+'/start')

        # global context_camera
        # # update the Context, publish new actuator status on data_out, send result
        # ngsiLdEntity = {"id": id_LD,
        #                 "type": v_thing_type_attr[-1],
        #                 "@context": [ "https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld" ]
        #                 }
        # data = [ngsiLdEntity]
        # context_camera[-1].update(data)
        
        # # publish changed status
        # message = {"data": data, "meta": {
        #     "vThingID": v_thing_ID[-1]}}  # neutral-format
        # self.publish(message)

        # publish command result
        if "cmd-qos" in cmd_info:
            if int(cmd_info['cmd-qos']) > 0:
                self.send_commandResult(cmd_name, cmd_info, id_LD, "OK")
    
    def on_stop(self, cmd_name, cmd_info, id_LD, actuatorThread):
        print("Sending stop command to robot")
        _robot_ip, _robot_port=self.get_robot_ip_port()
        print("ip: "+_robot_ip+"  port: "+_robot_port)
        requests.get("http://"+_robot_ip+':'+_robot_port+'/stop')
        
        # publish command result
        if "cmd-qos" in cmd_info:
            if int(cmd_info['cmd-qos']) > 0:
                self.send_commandResult(cmd_name, cmd_info, id_LD, "OK")

    def publish(self, message, topic=""):
        msg=json.dumps(message)
        if topic == "":
            out_topic = v_thing_topic[-1] + '/' + out_data_suffix
        else:
            out_topic = topic
        #msg = str(message).replace("\'", "\"")
        print("Message sent on "+out_topic + "\n" + msg+"\n")
        # publish data to out_topic
        mqtt_data_client.publish(out_topic, msg)

    def on_message_data_in_vThing(self, mosq, obj, msg):
        payload = msg.payload.decode("utf-8", "ignore")
        print("Message received on "+msg.topic + "\n" + payload+"\n")
        jres = json.loads(payload.replace("\'", "\""))
        try:
            data = jres["data"]
            for entity in data:
                id_LD = entity["id"]
                #if id_LD != v_thing_ID_LD[-1]:
                #    print("Entity not handled by the Thingvisor, message dropped")
                #    continue
                i=get_vthing_index(id_LD)
                for cmd in commands[i]:
                    if cmd in entity:
                        self.receive_commandRequest(entity)
                        continue
            return
        except Exception as ex:
            traceback.print_exc()
        return


    # mqtt client for sending data
    def __init__(self):
        Thread.__init__(self)

    def run(self):
        global commands

        print("Thread mqtt data started")
        global mqtt_data_client
        mqtt_data_client.connect(MQTT_data_broker_IP, MQTT_data_broker_port, 30)

        # Create initial status
        commands = []
        for i in range(num_of_cameras+1):
            if i==num_of_cameras:
                commands.append(["start","stop"])
            else:
                commands.append(["set_caching"])

            ngsiLdEntity = {"id": v_thing_ID_LD[i],
                        "type": v_thing_type_attr[i],
                        "commands": {"type": "Property", "value": commands[i]},
                        "@context": [ "https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld" ]
                        }
            data = [ngsiLdEntity]
            context_camera[i].set_all(data)

            mqtt_data_client.message_callback_add(v_thing_topic[i] + "/" + in_data_suffix,
                                                self.on_message_data_in_vThing)
            mqtt_data_client.subscribe(
                v_thing_topic[i] + "/" + in_data_suffix)

        mqtt_data_client.loop_forever()
        print("Thread '" + self.name + "' terminated")


class MqttControlThread(Thread):
    def on_message_get_thing_context(self, jres,i):
        silo_id = jres["vSiloID"]
        message = {"command": "getContextResponse", "data": context_camera[i].get_all(), "meta": {"vThingID": v_thing_ID[i]}}
        mqtt_control_client.publish(v_silo_prefix + "/" + silo_id + "/" + in_control_suffix, json.dumps(message))

    def send_destroy_v_thing_message(self,i):
        msg = {"command": "deleteVThing", "vThingID": v_thing_ID[i], "vSiloID": "ALL"}
        mqtt_control_client.publish(v_thing_prefix + "/" + v_thing_ID[i] + "/" + out_control_suffix, json.dumps(msg))
        return

    def send_destroy_thing_visor_ack_message(self):
        msg = {"command": "destroyTVAck", "thingVisorID": thing_visor_ID}
        mqtt_control_client.publish(tv_control_prefix + "/" + thing_visor_ID + "/" + out_control_suffix, json.dumps(msg))
        return

    def on_message_destroy_thing_visor(self, jres):
        global db_client
        db_client.close()
        for i in range(num_of_cameras+1):
            self.send_destroy_v_thing_message(i)
        self.send_destroy_thing_visor_ack_message()
        print("Shutdown completed")

    def on_message_update_thing_visor(self, jres):
        global robot_ip, robot_port, num_of_cameras

        print("Print update_info:", jres['update_info'])
        if 'num_of_cameras' in jres['params']:
            num_of_cameras = jres['params']['num_of_cameras']
            init()
        if 'robot_ip' in jres['params']:
            robot_ip=jres['params']['robot_ip']
        if 'robot_port' in jres['params']:
            robot_port=jres['params']['robot_port']

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
            i=get_vthing_index(name)
            if command_type == "getContextRequest":
                self.on_message_get_thing_context(jres,i)
        except Exception as ex:
            traceback.print_exc()
        return

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

        except Exception as ex:
            traceback.print_exc()
        return 'invalid command'

    def run(self):
        print("Thread mqtt control started")
        global mqtt_control_client
        mqtt_control_client.connect(MQTT_control_broker_IP, MQTT_control_broker_port, 30)

        # Publish on the thingVisor out_control topic the createVThing command and other parameters
        for i in range(num_of_cameras+1):
            v_thing_message = {"command": "createVThing",
                            "thingVisorID": thing_visor_ID,
                            "vThing": v_thing[i]}

            mqtt_control_client.publish(tv_control_prefix + "/" + thing_visor_ID + "/" + out_control_suffix,
                                        json.dumps(v_thing_message))
        time.sleep(6)

        # create vthings endpoint through REST
        global controller_url, tenant_id, admin_psw     
        for i in range(num_of_cameras):
            rest.set_vthing_endpoint(controller_url, v_thing_ID[i], "http://localhost:5000/cameras/"+str(i)+"/image", tenant_id, admin_psw)
        #rest.set_vthing_endpoint(controller_url, v_thing_ID[num_of_cameras], "http://localhost:5000/robot/"+str(0), tenant_id, admin_psw)


        # Add message callbacks that will only trigger on a specific subscription match
        for i in range(num_of_cameras+1):
            mqtt_control_client.message_callback_add(v_thing_topic[i] + "/" + in_control_suffix,
                                                    self.on_message_in_control_vThing)
        mqtt_control_client.message_callback_add(tv_control_prefix + "/" + thing_visor_ID + "/" + in_control_suffix,
                                                 self.on_message_in_control_TV)
        for i in range(num_of_cameras+1):
            mqtt_control_client.subscribe(v_thing_topic[i] + '/' + in_control_suffix)
        mqtt_control_client.subscribe(tv_control_prefix + "/" + thing_visor_ID + "/" + in_control_suffix)
        mqtt_control_client.loop_forever()
        print("Thread '" + self.name + "' terminated")


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

    
    num_of_cameras = 10
    robot_ip=None
    robot_port=None
    controller_url=None
    tenant_id=None
    admin_psw=None

    if params:
        if 'num_of_cameras' in params:
            num_of_cameras = params['num_of_cameras']
        if 'robot_ip' in params:
            robot_ip = params['robot_ip']
        if 'robot_port' in params:
            robot_port = params['robot_port']
        if 'controller_url' in params:
            controller_url = params['controller_url']
        if 'tenant_id' in params:
            tenant_id = params['tenant_id']
        if 'admin_psw' in params:
            admin_psw = params['admin_psw']


    v_thing_ID=[]
    v_thing_label=[]
    v_thing_description=[]
    v_thing=[]
    v_thing_name=[]
    v_thing_type_attr=[]
    v_thing_caching=[]
    for i in range(num_of_cameras):
        v_thing_name.append("camera"+str(i))
        v_thing_type_attr.append("Camera")
        v_thing_ID.append(thing_visor_ID + "/" + "camera"+str(i))
        v_thing_label.append("camera"+str(i))
        v_thing_description.append("cameraBot virtual thing")
        v_thing.append({"label": v_thing_label[i],
                "id": v_thing_ID[i],
                "description": v_thing_description[i]})
        v_thing_caching.append(False)
    
    v_thing_name.append("robot")
    v_thing_type_attr.append("Robot")
    v_thing_ID.append(thing_visor_ID + "/" + "robot")
    v_thing_label.append("robot")
    v_thing_description.append("cameraBot virtual thing")
    v_thing.append({"label": v_thing_label[-1],
            "id": v_thing_ID[-1],
            "description": v_thing_description[-1]})

    v_thing_ID_LD=[]
    for i in range(num_of_cameras+1):
        v_thing_ID_LD.append("urn:ngsi-ld:"+thing_visor_ID+":" + v_thing_name[i])
        

    # Context is a "map" of current virtual thing state
    # mapping of virtual thing with its context object. Useful in case of multiple virtual things
    context_camera = []
    contexts={}
    for i in range(num_of_cameras+1):
        context_camera.append(Context())
        contexts[v_thing_ID[i]]=context_camera[i]

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

    # set v_thing_topic the name of mqtt topic on witch publish vThing data
    # e.g vThing/helloWorld/hello
    v_thing_topic=[]
    for i in range(num_of_cameras+1):
        v_thing_topic.append(v_thing_prefix + "/" + v_thing_ID[i])

    # threadPoolExecutor of size one to handle one command at a time in a fifo order
    executor = ThreadPoolExecutor(1)

    mqtt_control_thread = MqttControlThread()  # mqtt control thread
    mqtt_control_thread.start()

    mqtt_data_thread = mqttDataThread()  # mqtt data thread
    mqtt_data_thread.start()

    def on_post_PATCH_cameras(request,lookup):
        rdata=request.form.to_dict()
        data=json.loads(lookup.get_data())

        if '_id' in data:
            index=data['_id']
            print(rdata)
            #message = {"url": "/cameras/"+str(index), "meta": {"vThingID": v_thing_ID[index]}}

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

    app.on_post_PATCH_cameras += on_post_PATCH_cameras

    # runs eve
    app.run(debug=False,host='0.0.0.0',port='5000')

    # while True:
    #     try:
    #         time.sleep(3)
    #     except:
    #         print("KeyboardInterrupt"+"\n")
    #         time.sleep(1)
    #         os._exit(1)
