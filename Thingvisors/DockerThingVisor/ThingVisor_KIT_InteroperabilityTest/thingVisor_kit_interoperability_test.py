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
import traceback
import datetime
import paho.mqtt.client as mqtt
import requests
from threading import Thread
from pymongo import MongoClient
from context import Context
import MobiusOperation

# -*- coding: utf-8 -*-

class FetcherThread(Thread):    
    # Thread used to fetch and publish data
    def __init__(self):
        Thread.__init__(self)

        # Create initial status
        location = "KIT"
        sensor = "Test01"
        sensor_type = "test"
        app = "detectedObject"

        vThingID = v_thing_ID

        data = [{"id":"null", "score": "null", "bbox": "null"}]

        ngsiLdEntity1 = {"id": "urn:ngsi-ld:"+location+":"+sensor,
                         "type": sensor_type,
                         app: {"type": "Property", "value": str(data)}
                        }

        # set initial context for hello virtual thing
        context_hello.set_all([ngsiLdEntity1])

    def run(self):
        location="KIT"
        sensor_type= "weather"
        app="detectedObject"
        virtual_sensor_name = 'WeatherSensor'

        mobius_resource_name = 'ZigBee_001'
        mobius_sensor_names = [
            # 'Coordinator', 
            'Router01', 
            'EndDevice01', 
            'EndDevice02'
        ]
        ipaddr = '192.168.37.102'
        port = '7579'
        mobius_url = r'http://' + ipaddr + ':' + port + r'/Mobius'
        
        ae_id = MobiusOperation.ae_get(mobius_url, mobius_resource_name).json()['m2m:ae']['aei']
        time.sleep(1)

        sensor_infos_mobius = [
            {
                'location':location, 
                'sensor_type':sensor_type, 
                'virtual_sensor_name': virtual_sensor_name,
                'resource_name': mobius_resource_name, 
                'real_sensor_name': mobius_sensor_name, 
                'ae_id': ae_id
            } for mobius_sensor_name in mobius_sensor_names
        ]

        fiware_url = "http://202.13.160.82:1026/v2/entities/"
        sensor_infos_fiware = [
            {
                "location":"KIT",
                "virtual_sensor_name":virtual_sensor_name,
                "sensor_type": sensor_type,
                "real_sensor_name":"BME280",
                "real_sensor_number": "001"
            }
        ]

        sensor_infos_tmp = list()
        serial_number = 1
        for sensor_info_mobius in sensor_infos_mobius:
            sensor_info_mobius['virtual_sensor_number'] = '{0:04}'.format(serial_number)
            serial_number += 1
            sensor_infos_tmp.append(sensor_info_mobius)
        sensor_infos_mobius = sensor_infos_tmp

        sensor_infos_tmp = list()
        for sensor_info_fiware in sensor_infos_fiware:
            sensor_info_fiware['virtual_sensor_number'] = '{0:04}'.format(serial_number)
            sensor_infos_tmp.append(sensor_info_fiware)
            serial_number += 1

        def get_mobius(mobius_url, sensor_info, app):
            response = MobiusOperation.get_sensor_data(mobius_url, sensor_info['resource_name'], sensor_info['real_sensor_name'], sensor_info['ae_id'])

            if response.status_code != 200:
                return

            result = response.json()
            data = result['m2m:cin']['con']

            dateissued = dict()
            dateissued['type']  = 'TimeData'
            dateissued['value'] = data['time'].split('.')[:-1][0]
            dateissued['metadata'] = dict()

            location_tmp = data['location'].replace(' ', '').split(',')
            location                         = dict()
            location['type']                 = 'geo:json'
            location['value']                = dict()
            location['value']['type']        = 'Point'
            location['value']['coordinates'] = [float(location_tmp[1]), float(location_tmp[0])]
            location['metadata'] = dict()

            room = dict()
            room['type']  = 'RoomNumber'
            room['value'] = data['room_number']
            room['metadata'] = dict()

            temperature = dict()
            temperature['type']  = 'Temperature'
            temperature['value'] = round(data['temperature'], 2)
            temperature['metadata'] = dict()

            humidity = dict()
            humidity['type']  = 'Humidity'
            humidity['value'] = round(data['humidity'], 2)
            humidity['metadata'] = dict()

            atmosphere = dict()
            atmosphere['type']  = 'Atmosphere'
            atmosphere['value'] = round(data['atmosphere'], 2)
            atmosphere['metadata'] = dict()

            data = dict()
            data['room']        = room
            data['location']    = location
            data['temperature'] = temperature
            data['humidity']    = humidity
            data['atmosphere']  = atmosphere
            data['dateissued']  = dateissued


            ngsiLdEntity = {"id": "urn:ngsi-ld:" + sensor_info['location'] + sensor_info['virtual_sensor_name'] + ':' + sensor_info['virtual_sensor_number'],
                             "type": sensor_info['sensor_type'],
                             app: {"type": "Property", "value":data}}
            return ngsiLdEntity

        def get_fiware(sensor_info, data):
            del data['id'], data['type'], data['name']
            data['dateissued']['value'] = data['dateissued']['value'].split('.')[:-1][0]

            data_tmp = dict()
            data_tmp['room']        = data['room']
            data_tmp['location']    = data['location']
            data_tmp['temperature'] = data['temperature']
            data_tmp['humidity']    = data['humidity']
            data_tmp['atmosphere']  = data['atmosphere']
            data_tmp['dateissued']  = data['dateissued']

            data = data_tmp

            ngsiLdEntity = {"id": "urn:ngsi-ld:" + sensor_info['location'] + sensor_info['virtual_sensor_name'] + ':' + sensor_info['virtual_sensor_number'],
                            "type": sensor_info["sensor_type"],
                            'detectobject': {'type': 'Property', 'value':data}}
            return ngsiLdEntity

        def pub(ngsiLdEntity):
            # update context status for virtual thing hello
            context_hello.update([ngsiLdEntity])

            # publish changed entities
            message = {"data": [ngsiLdEntity], "meta": {"vThingID": v_thing_ID}}
            print(str(message))

            mqtt_data_client.publish(v_thing_topic + '/' + v_thing_data_suffix, str(message).replace("\'","\""))
            #self.publish(message)

        while True:
            try:
                for sensor_info_mobius in sensor_infos_mobius:
                    ngsiLdEntity = get_mobius(mobius_url, sensor_info_mobius, app)
                    if ngsiLdEntity is not None:
                        pub(ngsiLdEntity)
                    time.sleep(1)  # possible fetch interval
            except:
                time.sleep(1)

            try:
                response = requests.get(fiware_url)
                if response.status_code != 200:
                    continue

                for sensor_info_fiware in sensor_infos_fiware:
                    for data in response.json():
                        if data["id"] == "urn:ngsi-ld:" + sensor_info_fiware["real_sensor_name"] + ":" + sensor_info_fiware["real_sensor_number"]:
                            ngsiLdEntity = get_fiware(sensor_info_fiware, data)
                            break
                    if ngsiLdEntity is not None:
                        pub(ngsiLdEntity)
                    time.sleep(1)  # possible fetch interval
            except:
                time.sleep(1)

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
        message = {"command": "getContextResponse", "data": context_hello.get_all(), "meta": {"vThingID": v_thing_ID}}
        mqtt_control_client.publish(v_silo_prefix + "/" + silo_id + "/" + in_control_suffix, str(message).replace("\'", "\""))

    def send_destroy_v_thing_message(self):
        msg = {"command": "deleteVThing", "vThingID": v_thing_ID, "vSiloID": "ALL"}
        mqtt_control_client.publish(v_thing_prefix + "/" + v_thing_ID + "/" + out_control_suffix, str(msg).replace("\'", "\""))
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
                           "vThing": v_thing}
        mqtt_control_client.publish(tv_control_prefix + "/" + thing_visor_ID + "/" + out_control_suffix,
                                    str(v_thing_message).replace("\'", "\""))

        # Add message callbacks that will only trigger on a specific subscription match
        mqtt_control_client.message_callback_add(v_thing_topic + "/" + in_control_suffix,
                                                 self.on_message_in_control_vThing)
        mqtt_control_client.message_callback_add(tv_control_prefix + "/" + thing_visor_ID + "/" + in_control_suffix,
                                                 self.on_message_in_control_TV)
        mqtt_control_client.subscribe(v_thing_topic + '/' + in_control_suffix)
        mqtt_control_client.subscribe(tv_control_prefix + "/" + thing_visor_ID + "/" + in_control_suffix)
        mqtt_control_client.loop_forever()
        print("Thread '" + self.name + "' terminated")


# main
if __name__ == '__main__':
    # v_thing_ID = os.environ["vThingID_0"]
    thing_visor_ID = os.environ["thingVisorID"]
    v_thing_ID = thing_visor_ID + "/" + "interoperability"
    v_thing_label = "interoperability-test"
    v_thing_description = "test interoperability ThingVisor"
    v_thing = {"label": v_thing_label,
               "id": v_thing_ID,
               "description": v_thing_description}
    MQTT_data_broker_IP = os.environ["MQTTDataBrokerIP"]
    MQTT_data_broker_port = int(os.environ["MQTTDataBrokerPort"])
    MQTT_control_broker_IP = os.environ["MQTTControlBrokerIP"]
    MQTT_control_broker_port = int(os.environ["MQTTControlBrokerPort"])
    parameters = os.environ["params"].replace("'", '"')
    if parameters:
        try:
            params = json.loads(parameters)
        except json.decoder.JSONDecodeError:
            # TODO manage exception
            print("error on params (JSON) decoding")

    # Context is a "map" of current virtual thing state
    context_hello = Context()
    # mapping of virtual thing with its context object. Useful in case of multiple virtual things
    contexts = {v_thing_ID: context_hello}

    # mqtt settings
    tv_control_prefix = "TV"  # prefix name for controller communication topic
    v_thing_prefix = "vThing"  # prefix name for virtual Thing data and control topics
    v_thing_data_suffix = "data_out"
    in_control_suffix = "c_in"
    out_control_suffix = "c_out"
    v_silo_prefix = "vSilo"

    # Mongodb settings
    time.sleep(1.5)  # wait before query the system database
    db_name = "viriotDB"  # name of system database
    thing_visor_collection = "thingVisorC"
    db_IP = os.environ['systemDatabaseIP']  # IP address of system database
    db_port = os.environ['systemDatabasePort']  # port of system database
    db_client = MongoClient('mongodb://' + db_IP + ':' + str(db_port) + '/')
    db = db_client[db_name]
    port_mapping = db[thing_visor_collection].find_one({"thingVisorID": thing_visor_ID}, {"port": 1, "_id": 0})
    print("port mapping: " + str(port_mapping))

    mqtt_control_client = mqtt.Client()
    mqtt_data_client = mqtt.Client()

    # set v_thing_topic the name of mqtt topic on witch publish vThing data
    # e.g vThing/helloWorld/hello
    v_thing_topic = v_thing_prefix + "/" + v_thing_ID

    data_thread = FetcherThread()  # Thread used to fetch data
    data_thread.start()

    mqtt_control_thread = MqttControlThread()  # mqtt control thread
    mqtt_control_thread.start()

    mqtt_data_thread = mqttDataThread()  # mqtt data thread
    mqtt_data_thread.start()
    while True:
        try:
            time.sleep(3)
        except:
            print("KeyboardInterrupt")
            time.sleep(1)
            os._exit(1)


