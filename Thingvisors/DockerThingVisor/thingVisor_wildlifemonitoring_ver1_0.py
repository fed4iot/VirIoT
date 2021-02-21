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

# Fed4IoT Thing ThingVisor Wildlife Monitoring

# Author : Kazuki Shigemori(Kanazawa Institute of Technology)
# Version : 1.0.0
# Day : 2021/02/01

import time
import os
import random
import json
import traceback
import paho.mqtt.client as mqtt
import requests
from threading import Thread
from pymongo import MongoClient
from context import Context

# -*- coding: utf-8 -*-

class FetcherThread(Thread):    
    def run(self):
        while True:
            location = "KIT"
            app = "detectedObject"

            #1
            sensor1 = "Hygrometer"
            sensorType1 = "hygrometer"
            url1 = "http://202.13.160.82:1026/v2/entities/urn:ngsi-ld:HakusanHygrometer:001"

            response = requests.get(url1)
            result = response.json()
            data1 = result

            ngsiLdEntity1 = {"id": "urn:ngsi-ld:"+location+":"+sensor1,
                             "type": sensorType1,
                             app: {"type": "Property", "value":data1}}

            #2
            sensor2 = "RainGauge"
            sensorType2 = "raingauge"
            url2 = "http://202.13.160.82:1026/v2/entities/urn:ngsi-ld:HakusanRainGauge:001"

            response = requests.get(url2)
            result = response.json()
            data2 = result

            ngsiLdEntity2 = {"id": "urn:ngsi-ld:"+location+":"+sensor2,
                             "type": sensorType2,
                             app: {"type": "Property", "value":data2}}
            
            #3
            sensor3 = "Illuminometer"
            sensorType3 = "illuminometer"
            url3 = "http://202.13.160.82:1026/v2/entities/urn:ngsi-ld:HakusanIlluminometer:001"

            response = requests.get(url3)
            result = response.json()
            data3 = result

            ngsiLdEntity3 = {"id": "urn:ngsi-ld:"+location+":"+sensor3,
                             "type": sensorType3,
                             app: {"type": "Property", "value":data3}}

            #4
            sensor4 = "AnimalDetector01"
            sensorType4 = "animalDetector"
            url4 = "http://202.13.160.82:1026/v2/entities/urn:ngsi-ld:HakusanAnimalDetector1:001"

            response = requests.get(url4)
            result = response.json()
            data4 = result

            ngsiLdEntity4 = {"id": "urn:ngsi-ld:"+location+":"+sensor4,
                             "type": sensorType4,
                             app: {"type": "Property", "value":data4}}

            #5
            sensor5 = "AnimalDetector02"
            url5 = "http://202.13.160.82:1026/v2/entities/urn:ngsi-ld:HakusanAnimalDetector3:001"

            response = requests.get(url5)
            result = response.json()
            data5 = result

            ngsiLdEntity5 = {"id": "urn:ngsi-ld:"+location+":"+sensor5,
                             "type": sensorType4,
                             app: {"type": "Property", "value":data5}}

            # update context status for virtual thing hello
            context_hello.update([ngsiLdEntity1])
            context_hello.update([ngsiLdEntity2])
            context_hello.update([ngsiLdEntity3])
            context_hello.update([ngsiLdEntity4])
            context_hello.update([ngsiLdEntity5])

            # publish changed entities
            message1 = {"data": [ngsiLdEntity1], "meta": {"vThingID": v_thing_ID1}}
            print(str(message1))
            message2 = {"data": [ngsiLdEntity2], "meta": {"vThingID": v_thing_ID2}}
            print(str(message2))
            message3 = {"data": [ngsiLdEntity3], "meta": {"vThingID": v_thing_ID3}}
            print(str(message3))
            message4 = {"data": [ngsiLdEntity4], "meta": {"vThingID": v_thing_ID4}}
            print(str(message4))
            message5 = {"data": [ngsiLdEntity5], "meta": {"vThingID": v_thing_ID4}}
            print(str(message5))

            mqtt_data_client.publish(v_thing_topic1 + '/' + v_thing_data_suffix, str(message1).replace("\'","\""))
            mqtt_data_client.publish(v_thing_topic2 + '/' + v_thing_data_suffix, str(message2).replace("\'","\""))
            mqtt_data_client.publish(v_thing_topic3 + '/' + v_thing_data_suffix, str(message3).replace("\'","\""))
            mqtt_data_client.publish(v_thing_topic4 + '/' + v_thing_data_suffix, str(message4).replace("\'","\""))
            mqtt_data_client.publish(v_thing_topic4 + '/' + v_thing_data_suffix, str(message5).replace("\'","\""))

            time.sleep(2)  # possible fetch interval

class mqttDataThread(Thread):
    # mqtt client for sending data
    def __init__(self):
        Thread.__init__(self)

    def run(self):
        print("Thread mqtt data started")
        global mqtt_data_client
        mqtt_data_client.connect(MQTT_data_broker_IP, MQTT_data_broker_port, 30)
        mqtt_data_client.loop_forever()
        print("Thread '" + self.name + "' terminated")

class MqttControlThread(Thread):

    def on_message_get_thing_context(self, jres):
        silo_id = jres["vSiloID"]
        message = {"command": "getContextResponse", "data": context_hello.get_all(), 
                   "meta": {"vThingID1": v_thing_ID1, "vThingID2": v_thing_ID2, "vThingID3": v_thing_ID3, "vThingID4": v_thing_ID4}}
        mqtt_control_client.publish(v_silo_prefix + "/" + silo_id + "/" + in_control_suffix, str(message).replace("\'", "\""))

    def send_destroy_v_thing_message(self):
        msg = {"command": "deleteVThing", "vThingID": v_thing_ID1, "vSiloID": "ALL"}
        mqtt_control_client.publish(v_thing_prefix + "/" + v_thing_ID1 + "/" + out_control_suffix, str(msg).replace("\'", "\""))
        msg = {"command": "deleteVThing", "vThingID": v_thing_ID2, "vSiloID": "ALL"}
        mqtt_control_client.publish(v_thing_prefix + "/" + v_thing_ID2 + "/" + out_control_suffix, str(msg).replace("\'", "\""))
        msg = {"command": "deleteVThing", "vThingID": v_thing_ID3, "vSiloID": "ALL"}
        mqtt_control_client.publish(v_thing_prefix + "/" + v_thing_ID3 + "/" + out_control_suffix, str(msg).replace("\'", "\""))
        msg = {"command": "deleteVThing", "vThingID": v_thing_ID4, "vSiloID": "ALL"}
        mqtt_control_client.publish(v_thing_prefix + "/" + v_thing_ID4 + "/" + out_control_suffix, str(msg).replace("\'", "\""))
        return

    def send_destroy_thing_visor_ack_message(self):
        msg = {"command": "destroyTVAck", "thingVisorID": thing_visor_ID}
        mqtt_control_client.publish(tv_control_prefix + "/" + thing_visor_ID + "/" + out_control_suffix, str(msg).replace("\'", "\""))
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
        jres = json.loads(payload.replace("\'", "\""))
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
        jres = json.loads(payload.replace("\'", "\""))
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

        # Publish on the thingVisor out_control topic the createVThing command and other parameters
        v_thing_message = {"command": "createVThing",
                           "thingVisorID": thing_visor_ID,
                           "vThing1": v_thing1, "vThing2": v_thing2, "vThing3": v_thing3, "vThing4": v_thing4, "vThing5": v_thing5}
        mqtt_control_client.publish(tv_control_prefix + "/" + thing_visor_ID + "/" + out_control_suffix,
                                    str(v_thing_message).replace("\'", "\""))

        # Add message callbacks that will only trigger on a specific subscription match
        mqtt_control_client.message_callback_add(v_thing_topic1 + "/" + in_control_suffix,
                                                 self.on_message_in_control_vThing)
        mqtt_control_client.message_callback_add(v_thing_topic2 + "/" + in_control_suffix,
                                                 self.on_message_in_control_vThing)
        mqtt_control_client.message_callback_add(v_thing_topic3 + "/" + in_control_suffix,
                                                 self.on_message_in_control_vThing)
        mqtt_control_client.message_callback_add(v_thing_topic4 + "/" + in_control_suffix,
                                                 self.on_message_in_control_vThing)
        mqtt_control_client.message_callback_add(tv_control_prefix + "/" + thing_visor_ID + "/" + in_control_suffix,
                                                 self.on_message_in_control_TV)
        mqtt_control_client.subscribe(v_thing_topic1 + '/' + in_control_suffix)
        mqtt_control_client.subscribe(tv_control_prefix + "/" + thing_visor_ID + "/" + in_control_suffix)
        mqtt_control_client.loop_forever()
        print("Thread '" + self.name + "' terminated")

# main
if __name__ == '__main__':
    thing_visor_ID = os.environ["thingVisorID"]

    #v_thing_ID = thing_visor_ID + "/" + "hello"
    v_thing_ID1 = thing_visor_ID + "/" + "hygrometer"
    v_thing_ID2 = thing_visor_ID + "/" + "raingauge"
    v_thing_ID3 = thing_visor_ID + "/" + "illuminometer"
    v_thing_ID4 = thing_visor_ID + "/" + "animaldetector"

    v_thing_label = "kit-test"
    #v_thing_description = "hello world virtual thing"
    #v_thing = {"label": v_thing_label,
    #           "id": v_thing_ID,
    #           "description": v_thing_description}
    v_thing1 = {"label": v_thing_label,
                "id": v_thing_ID1,
                "description": "Hygrometer"}
    v_thing2 = {"label": v_thing_label,
                "id": v_thing_ID2,
                "description": "Rain Gauge"}
    v_thing3 = {"label": v_thing_label,
                "id": v_thing_ID3,
                "description": "Illuminometer"}
    v_thing4 = {"label": v_thing_label,
                "id": v_thing_ID4,
                "description": "Animal Detector 01"}
    v_thing5 = {"label": v_thing_label,
                "id": v_thing_ID4,
                "description": "Animal Detector 02"}

    MQTT_data_broker_IP = os.environ["MQTTDataBrokerIP"]
    MQTT_data_broker_port = int(os.environ["MQTTDataBrokerPort"])
    MQTT_control_broker_IP = os.environ["MQTTControlBrokerIP"]
    MQTT_control_broker_port = int(os.environ["MQTTControlBrokerPort"])

    parameters = os.environ["params"].replace("'", '"')

    if parameters:
        try:
            params = json.loads(parameters)
        except json.decoder.JSONDecodeError:
            print("error on params (JSON) decoding")  # TODO manage exception

    context_hello = Context()               # Context is a "map" of current virtual thing state
    contexts = {v_thing_ID1: context_hello} # mapping of virtual thing with its context object. Useful in case of multiple virtual things
    contexts = {v_thing_ID2: context_hello}
    contexts = {v_thing_ID3: context_hello}
    contexts = {v_thing_ID4: context_hello}
   
    # mqtt settings
    tv_control_prefix = "TV"   # prefix name for controller communication topic
    v_thing_prefix = "vThing"  # prefix name for virtual Thing data and control topics
    v_thing_data_suffix = "data_out"
    in_control_suffix = "c_in"
    out_control_suffix = "c_out"
    v_silo_prefix = "vSilo"

    # Mongodb settings
    time.sleep(1.5)                             # wait before query the system database
    db_name = "viriotDB"                        # name of system database
    thing_visor_collection = "thingVisorC"
    db_IP = os.environ['systemDatabaseIP']      # IP address of system database
    db_port = os.environ['systemDatabasePort']  # port of system database
    db_client = MongoClient('mongodb://' + db_IP + ':' + str(db_port) + '/')
    db = db_client[db_name]
    port_mapping = db[thing_visor_collection].find_one({"thingVisorID": thing_visor_ID}, {"port": 1, "_id": 0})
    print("port mapping: " + str(port_mapping))

    mqtt_control_client = mqtt.Client()
    mqtt_data_client = mqtt.Client()

    # set v_thing_topic the name of mqtt topic on witch publish vThing data
    # e.g vThing/helloWorld/hello
    #v_thing_topic = v_thing_prefix + "/" + v_thing_ID
    v_thing_topic1 = v_thing_prefix + "/" + v_thing_ID1
    v_thing_topic2 = v_thing_prefix + "/" + v_thing_ID2
    v_thing_topic3 = v_thing_prefix + "/" + v_thing_ID3
    v_thing_topic4 = v_thing_prefix + "/" + v_thing_ID4

    data_thread = FetcherThread()              # Thread used to fetch data
    data_thread.start()

    mqtt_control_thread = MqttControlThread()  # mqtt control thread
    mqtt_control_thread.start()

    mqtt_data_thread = mqttDataThread()        # mqtt data thread
    mqtt_data_thread.start()

    while True:
        try:
            time.sleep(3)
        except:
            print("KeyboardInterrupt")
            time.sleep(1)
            os._exit(1)
