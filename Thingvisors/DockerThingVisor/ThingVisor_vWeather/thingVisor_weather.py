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

# Thing Hypervisor copying data from a oneM2M (Mobius) container
import traceback

import paho.mqtt.client as mqtt
import time
import os
from threading import Thread
import requests
import json
import urllib
from pymongo import MongoClient
from context import Context

# -*- coding: utf-8 -*-


class FetcherThread(Thread):
    def __init__(self):
        Thread.__init__(self)
        for city in cities:
            for v_thing in v_things:
                if v_thing['city'] != city:
                    continue
                v_thing_id = v_thing["vThing"]["id"]  # e.g. "vWeather/rome_temp"
                sens_type = v_thing["type"]  # key to search into response json, e.g. "temp"
                data = 0.0  # e.g. the temperature value
                data_type = v_thing["dataType"]  # e.g. "temperature"
                thing_name = v_thing["thing"]  # e.g. "thermometer"

                ngsi_ld_entity1 = {"@context":["https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld"],
                                   "id": "urn:ngsi-ld:" + city + ":" + sens_type,
                                   "type": data_type,
                                   thing_name: {"type": "Property", "value": data}}
                # set initial context
                contexts[v_thing_id].set_all([ngsi_ld_entity1])

    def run(self):
        while True:
            for city in cities:
                location = urllib.parse.quote(city)
                url = 'https://api.openweathermap.org/data/2.5/weather?q=' + location + '&appid=f5dd231b269189f270094476aa8399a5'
                try:
                    r = requests.get(url, timeout=1)
                except requests.exceptions.Timeout:
                    print("Request timed out - " + city)
                except Exception as ex:
                    print("Some Error with city " + city)
                    print(ex.with_traceback())
                for v_thing in v_things:
                    if v_thing['city'] != city:
                        continue
                    v_thing_id = v_thing["vThing"]["id"]        # e.g. "vWeather/rome_temp"
                    sens_type = v_thing["type"]                 # key to search into response json, e.g. "temp"
                    data = r.json()["main"][sens_type]     # e.g. the temperature value (A NUMBER)
                    data_type = v_thing["dataType"]             # e.g. "temperature"
                    thing_name = v_thing["thing"]               # e.g. "thermometer"

                    ngsi_ld_entity1 = {"@context":["https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld"],
                                       "id": "urn:ngsi-ld:" + city + ":" + sens_type,
                                       "type": data_type,
                                       thing_name: {"type": "Property", "value": data}}

                    contexts[v_thing_id].update([ngsi_ld_entity1])
                    message = {"data": [ngsi_ld_entity1], "meta": {"vThingID": v_thing_id}}
                    print(str(message))
                    # publish received data to data topic by using neutral format
                    mqtt_data_client.publish(v_thing["topic"] + '/'+v_thing_data_suffix, json.dumps(message))
                    time.sleep(0.2)
            time.sleep(refresh_rate)


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


class mqttControlThread(Thread):

    def on_message_get_thing_context(self, jres):
        silo_id = jres["vSiloID"]
        v_thing_id = jres["vThingID"]
        message = {"command": "getContextResponse", "data": contexts[v_thing_id].get_all(), "meta": {"vThingID": v_thing_id}}
        mqtt_control_client.publish(v_silo_prefix + "/" + silo_id + "/" + in_control_suffix, json.dumps(message))

    def send_destroy_v_thing_message(self):
        for v_thing in v_things:
            v_thing_ID = v_thing["vThing"]["id"]
            msg = {"command": "deleteVThing", "vThingID": v_thing_ID, "vSiloID": "ALL"}
            mqtt_control_client.publish(v_thing_prefix + "/" + v_thing_ID + "/" + out_control_suffix, json.dumps(msg))
        return

    def send_destroy_thing_visor_ack_message(self):
        msg = {"command": "destroyTVAck", "thingVisorID": thing_visor_ID}
        mqtt_control_client.publish(tv_control_prefix + "/" + thing_visor_ID + "/" + out_control_suffix, json.dumps(msg))
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

        # Publish on the thingVisor out_control topic the createVThing command and other parameters for each vThing
        for v_thing in v_things:
            v_thing_topic = v_thing["topic"]
            v_thing_message = {"command": "createVThing",
                               "thingVisorID": thing_visor_ID,
                               "vThing": v_thing["vThing"]}
            mqtt_control_client.publish(tv_control_prefix + "/" + thing_visor_ID + "/" + out_control_suffix,
                                        json.dumps(v_thing_message))

            # Add message callbacks that will only trigger on a specific subscription match
            mqtt_control_client.message_callback_add(v_thing_topic + "/" + in_control_suffix,
                                                     self.on_message_in_control_vThing)
            mqtt_control_client.message_callback_add(tv_control_prefix + "/" + thing_visor_ID + "/" + in_control_suffix,
                                                     self.on_message_in_control_TV)
            mqtt_control_client.subscribe(v_thing_topic + '/' + in_control_suffix)
            mqtt_control_client.subscribe(tv_control_prefix + "/" + thing_visor_ID + "/" + in_control_suffix)
            time.sleep(0.1)
        mqtt_control_client.loop_forever()
        print("Thread '" + self.name + "' terminated")


# main
if __name__ == '__main__':
    MAX_RETRY = 3

    thing_visor_ID = os.environ["thingVisorID"]

    # Mosquitto settings
    tv_control_prefix = "TV"  # prefix name for controller communication topic
    v_thing_prefix = "vThing"  # prefix name for virtual Thing data and control topics
    v_thing_data_suffix = "data_out"
    in_control_suffix = "c_in"
    out_control_suffix = "c_out"
    v_silo_prefix = "vSilo"
    mqtt_control_client = mqtt.Client()
    mqtt_data_client = mqtt.Client()

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
            params = json.loads(parameters.replace("'", '"'))

    except json.decoder.JSONDecodeError:
        print("error on params (JSON) decoding" + "\n")
        exit()
    except Exception as e:
        print("Error: Parameters not found in tv_entry", e)
        exit()


    # mapping of virtual thing with its context object. Useful in case of multiple virtual things
    contexts = {}

    cities = params["cities"]
    sensors = [{"id": "_temp", "type": "temp", "description": "current temperature, Kelvin",
                "dataType": "temperature", "thing": "thermometer"},
               {"id": "_humidity", "type": "humidity", "dataType": "humidity",
                "description": "current humidity, %", "thing": "hygrometer"},
               {"id": "_pressure", "type": "pressure", "dataType": "pressure",
                "description": "current atmospheric pressure, hPa", "thing": "barometer"}]

    # refresh_rate = int(params.get('rate','300'))
    if params and "rate" in params.keys():
        refresh_rate = params["rate"]
    else:
        refresh_rate = 300

    v_things = []
    for city in cities:
        for sens in sensors:
            thing = sens["thing"]
            label = sens["thing"] + " in " + str(city)
            identifier = thing_visor_ID + "/" + city+sens["id"]
            description = sens["description"]
            topic = v_thing_prefix + "/" + identifier
            v_things.append({"vThing": {"label": label, "id": identifier, "description": description},
                             "topic": v_thing_prefix + "/" + identifier, "type": sens["type"],
                             "dataType": sens["dataType"], "city": city, "thing": thing})
            contexts[identifier] = Context()

    port_mapping = db[thing_visor_collection].find_one({"thingVisorID": thing_visor_ID}, {"port": 1, "_id": 0})
    print("port mapping: " + str(port_mapping))

    data_thread = FetcherThread()  # Thread used to fetch data
    data_thread.start()

    mqtt_control_thread = mqttControlThread()  # mqtt control thread
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
