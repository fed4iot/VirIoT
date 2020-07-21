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

# Fed4IoT ThingVisor copying data from a oneM2M (Mobius) container

import sys
import traceback
import paho.mqtt.client as mqtt
import time
import os
import socket
import json
from threading import Thread
from pymongo import MongoClient
from context import Context
from flask import Flask
#from flask import json
from flask import request
# sys.path.insert(0, '/app/PyLib/')
sys.path.insert(0, 'PyLib/')


app = Flask(__name__)
flask_port = 8089


class httpRxThread(Thread):

    def __init__(self):
        Thread.__init__(self)

    def run(self):
        print("Thread Rx HTTP started")
        app.run(host='0.0.0.0', port=flask_port)
        print("Thread '" + self.name + " closed")

    @app.route('/notify', methods=['POST'])
    def recv_notify():
        try:
            r = request.get_json()
            if type(r) is dict:
                jres = r
            else:
                jres = json.loads(r)
            ngsiLdEntity1 = {"id": "urn:ngsi-ld:" + v_thing_ID_LD,"type": v_thing_type_attr}
            msg={}
            msg['type'] = "Property"
            msg['value'] = jres
            ngsiLdEntity1['msg']=msg
            context_vThing.update([ngsiLdEntity1])
            message = {"data": [ngsiLdEntity1], "meta": {"vThingID": v_thing_ID}}
            print("topic name: " + v_thing_topic + '/' + data_out_suffix + " ,message: " + json.dumps(message))
            mqtt_data_client.publish(v_thing_topic + '/' + data_out_suffix,json.dumps(message))
            return 'OK', 201

        except Exception as err:
            print("Bad notification format", err)
            return json.dumps({"message": 'Bad notification format'}), 401


class mqttDataThread(Thread):
    # mqtt client used for sending data
    def __init__(self):
        Thread.__init__(self)

    def run(self):
        print("Thread mqtt data started")
        ngsiLdEntity1 = {   "id": "urn:ngsi-ld:" + v_thing_ID_LD,
                                "type": v_thing_type_attr,
                                "msg": {"type": "Property", "value": {}}}
        context_vThing.update([ngsiLdEntity1])
        mqtt_data_client.connect(MQTT_data_broker_IP, MQTT_data_broker_port, 30)
        mqtt_data_client.loop_forever()
        print("Thread '" + self.name + "' terminated")

'''
class mqttRxThread(Thread):
    # mqtt client used for receiving and sending data
    def __init__(self):
        Thread.__init__(self)

    def on_message_in_rx(self, mosq, obj, msg):
        payload = msg.payload
        # payload = msg.payload.decode("utf-8", "ignore")
        # print("on_message_in_rx ---> msg -->", msg.topic + " " + payload)
        # print("payload --- ", json.loads(payload))
        # print("type payload --- ", type(json.loads(payload)))



        mqtt_VirIoT_client.publish(v_thing_topic + '/' + v_thing_data_out_suffix,
                                 payload=payload)

        
        # silo_id = jres["vSiloID"]
        # message = {"command": "getContextResponse", "data": context_vThing.get_all(), "meta": {"vThingID": v_thing_ID}}
        # mqtt_control_client.publish(v_silo_prefix + "/" + silo_id + "/" + in_control_suffix, str(message).replace("\'", "\""))

    def run(self):
        print("Thread mqtt ribbon started")
        global mqtt_ribbon_client
        mqtt_ribbon_client.connect(MQTT_VirIoT_data_broker_IP, MQTT_VirIoT_data_broker_port, 30)
        # Add message callbacks that will only trigger on a specific subscription match
        mqtt_ribbon_client.message_callback_add("ribbonTopic", self.on_message_in_rx)
        mqtt_ribbon_client.subscribe('ribbonTopic')
        mqtt_ribbon_client.loop_forever()
        print("Thread '" + self.name + "' terminated")

'''


class mqttControlThread(Thread):

    def on_message_get_thing_context(self, jres):
        silo_id = jres["vSiloID"]
        msg = {"command": "getContextResponse", "data": context_vThing.get_all(), "meta": {"vThingID": v_thing_ID}}
        mqtt_control_client.publish(v_silo_prefix + "/" + silo_id + "/" + control_in_suffix, json.dumps(msg))

    def send_destroy_v_thing_message(self):
        msg = {"command": "deleteVThing", "vThingID": v_thing_ID, "vSiloID": "ALL"}
        mqtt_control_client.publish(v_thing_prefix + "/" + v_thing_ID + "/" + control_out_suffix, json.dumps(msg))
        return

    def send_destroy_thing_visor_ack_message(self):
        msg = {"command": "destroyTVAck", "thingVisorID": thing_visor_ID}
        mqtt_control_client.publish(tv_control_prefix + "/" + thing_visor_ID + "/" + control_out_suffix, json.dumps(msg))
        return

    def on_message_destroy_thing_visor(self, jres):
        global db_client
        db_client.close()
        self.send_destroy_v_thing_message()
        self.send_destroy_thing_visor_ack_message()
        print("Shutdown completed")

    # handler for mqtt control topics
    def __init__(self):
        Thread.__init__(self)


    def on_message_in_control_vThing(self, mosq, obj, msg):
        payload = msg.payload.decode("utf-8", "ignore")
        print(msg.topic + " " + str(payload))
        # jres = json.loads(payload.replace("\'", "\""))
        jres = json.loads(payload)
        try:
            command_type = jres["command"]
            if command_type == "getContextRequest":
                self.on_message_get_thing_context(jres)
        except Exception as ex:
            traceback.print_exc()
        return


    def on_message_in_control_TV(self, mosq, obj, msg):
        payload = msg.payload.decode("utf-8", "ignore")
        print(msg.topic + " " + str(payload))
        jres = json.loads(payload)
        try:
            command_type = jres["command"]
            if command_type == "destroyTV":
                self.on_message_destroy_thing_visor(jres)
        except Exception as ex:
            traceback.print_exc()
        return 'invalid command'

    def run(self):
        print("Thread mqtt control started")
        global mqtt_control_client
        mqtt_control_client.connect(MQTT_control_broker_IP, MQTT_control_broker_port, 30)

        # Publish on the thingVisor out_control topic the add_vThing command and other parameters
        v_thing_message = {"command": "createVThing",
                           "thingVisorID": thing_visor_ID,
                           "vThing": v_thing}
        mqtt_control_client.publish(tv_control_prefix + "/" + thing_visor_ID + "/" + control_out_suffix,
                                    json.dumps(v_thing_message))
                                    # str(v_thing_message).replace("\'", "\""))

        # Add message callbacks that will only trigger on a specific subscription match
        mqtt_control_client.message_callback_add(v_thing_topic + "/" + control_in_suffix,
                                                 self.on_message_in_control_vThing)
        mqtt_control_client.message_callback_add(tv_control_prefix + "/" + thing_visor_ID + "/" + control_in_suffix,
                                                 self.on_message_in_control_TV)
        mqtt_control_client.subscribe(v_thing_topic + '/' + control_in_suffix)
        mqtt_control_client.subscribe(tv_control_prefix + "/" + thing_visor_ID + "/" + control_in_suffix)
        mqtt_control_client.loop_forever()
        print("Thread '" + self.name + "' terminated")


# main
if __name__ == '__main__':
    MAX_RETRY = 3
    resources_ip = "127.0.0.1"
    # Only for test
    '''
    os.environ = {'MQTTDataBrokerIP': resources_ip,
                    'MQTTDataBrokerPort': 1883,
                    'MQTTControlBrokerIP': resources_ip,
                    'MQTTControlBrokerPort': 1883,
                    'params': {},
                    'thingVisorID': 'ribbon-tv',
                    'systemDatabaseIP': "172.17.0.2",
                    'systemDatabasePort': 27017}
    '''

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
        MQTT_data_broker_IP = os.environ["MQTTDataBrokerIP"]
        MQTT_data_broker_port = int(os.environ["MQTTDataBrokerPort"])
        MQTT_control_broker_IP = os.environ["MQTTControlBrokerIP"]
        MQTT_control_broker_port = int(os.environ["MQTTControlBrokerPort"])
        params = tv_entry["params"]

    except json.decoder.JSONDecodeError:
        # TODO manage exception
        print("error on params (JSON) decoding")
        os._exit(1)
    except KeyError:
        print(Exception.with_traceback())
        os._exit(1)
    except Exception as err:
        print("ERROR on params (JSON)", err)

    if 'vThingName' in params.keys():
        v_thing_name = params['vThingName']
    else:
        v_thing_name = "vThingRelay"
    if 'vThingType' in params.keys():
        v_thing_type_attr = params['vThingType']
    else:
        v_thing_type_attr = "message"

    v_thing_label = v_thing_name
    v_thing_description = "Pass Through vThing"
    v_thing_ID = thing_visor_ID + "/" + v_thing_name
    v_thing_ID_LD = "urn:ngsi-ld:"+thing_visor_ID+":" + v_thing_name  # ID used in id field od ngsi-ld for data   
    v_thing = {"label": v_thing_label,
               "id": v_thing_ID,
               "description": v_thing_description}

    # MQTT_data_broker_IP = os.environ["MQTTDataBrokerIP"]
    # MQTT_data_broker_port = int(os.environ["MQTTDataBrokerPort"])
    # MQTT_control_broker_IP = os.environ["MQTTControlBrokerIP"]
    # MQTT_control_broker_port = int(os.environ["MQTTControlBrokerPort"])



    # sub_rn = v_thing_ID.replace("/",":") + "_subF4I"
    # vtype = ""

    # Context is a "map" of current virtual thing state
    context_vThing = Context()
    # mapping of virtual thing with its context object. Useful in case of multiple virtual things
    contexts = {v_thing_ID: context_vThing}

    # Mqtt settings
    tv_control_prefix = "TV"  # prefix name for controller communication topic
    v_thing_prefix = "vThing"  # prefix name for virtual Thing data and control topics
    data_out_suffix = "data_out"
    control_in_suffix = "c_in"
    control_out_suffix = "c_out"
    v_silo_prefix = "vSilo"

    # # Mongodb settings
    # time.sleep(1.5)  # wait before query the system database
    # db_name = "viriotDB"  # name of system database
    # thing_visor_collection = "thingVisorC"
    # db_IP = os.environ['systemDatabaseIP']  # IP address of system database
    # db_port = os.environ['systemDatabasePort']  # port of system database
    # db_client = MongoClient('mongodb://' + db_IP + ':' + str(db_port) + '/')
    # db = db_client[db_name]
    port_mapping = db[thing_visor_collection].find_one({"thingVisorID": thing_visor_ID}, {"port": 1, "_id": 0})
    poa_IP_dict = db[thing_visor_collection].find_one({"thingVisorID": thing_visor_ID}, {"IP": 1, "_id": 0})
    poa_IP = str(poa_IP_dict['IP'])
    print("poa_IP->", poa_IP)
    poa_port = port_mapping['port'][str(flask_port)+'/tcp']
    if not poa_IP:
        poa_IP = socket.gethostbyname(socket.gethostname())
    if not poa_port:
        poa_port = flask_port
    notification_URI = ["http://" + poa_IP + ":" + poa_port + "/notify"]

    # set v_thing_topic the name of mqtt topic on witch publish vThing data
    # e.g vThing/helloWorld/hello
    v_thing_topic = v_thing_prefix + "/" + v_thing_ID

    mqtt_control_client = mqtt.Client()
    mqtt_data_client = mqtt.Client()
    #mqtt_ribbon_client = mqtt.Client()

    rxThread = httpRxThread()  # http server used to receive JSON messages from external producer
    rxThread.start()

    mqtt_control_thread = mqttControlThread()       # mqtt VirIoT control thread
    mqtt_control_thread.start()

    mqtt_data_thread = mqttDataThread()       # mqtt VirIoT data thread
    mqtt_data_thread.start()

    #mqtt_ribbon_thread = mqttRxThread()             # mqtt data thread
    #mqtt_ribbon_thread.start()

    time.sleep(2)
    while True:
        try:
            time.sleep(3)
        except:
            print("KeyboardInterrupt")
            time.sleep(1)
            os._exit(1)
