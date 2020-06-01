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
from flask import json
from flask import request
sys.path.insert(0, '/app/PyLib/')
import F4Im2m

app = Flask(__name__)
flask_port = 8089


class httpThread(Thread):

    def __init__(self):
        Thread.__init__(self)

    def run(self):
        global vtype
        print("Thread http started")
        # fetch latest value from Mobius server
        value = "None"
        vtype = "None"
        ngsiLdEntities = []
        for cnt_arn in cnt_arns:
            try:
                status, cin = F4Im2m.get_cin_latest("Mobius/" + cnt_arn, origin, CSE_url)

                if status == 200:
                    try:
                        value = cin['m2m:cin']['con']
                    except:
                        print("No CIN in the container " + cnt_arn)
                else:
                    print("HTTP status code:", status)
                    print("No CIN in the container " + cnt_arn)
            except Exception as err:
                print("Error in F4Im2m.get_cin_latest:", err)

            try:
                status, cnt = F4Im2m.container_get("Mobius/" + cnt_arn, origin, CSE_url)
                if status == 200:
                    try:
                        lbl = cnt['m2m:cnt']['lbl']
                        vtype = lbl[0]
                        for i in range(1, len(lbl)):
                            vtype = vtype + "," + lbl[i]
                    except:
                        print("No labels for the container "+cnt_arn)
                else:
                    print("No labels for the container "+cnt_arn)
            except Exception as err:
                print("Error in F4Im2m.container_get:", err)

            ngsildentity_id = "urn:ngsi-ld:"+v_thing_name+':'+cnt_arn.replace('/', ':')
            ngsildentity_cnt_arn = cnt_arn.replace('/', ':')

            ngsiLdEntity1 = {"id": ngsildentity_id,
                             "type": vtype,
                             ngsildentity_cnt_arn: {"type": "Property", "value": value}}
            ngsiLdEntities.append(ngsiLdEntity1)

        data = ngsiLdEntities
        # set initial context for the virtual thing
        context_vThing.set_all(data)
        app.run(host='0.0.0.0', port=flask_port)
        print("Thread '" + self.name + " closed")

    @app.route('/notify', methods=['POST'])
    def recv_notify():
        global v_thing_ID
        jres = request.get_json()
        print("enter notify, POST body: " + json.dumps(jres))
        try:
            if 'm2m:sgn' in jres:
                sur = str(jres['m2m:sgn']['sur'])
                cnt_arn = '/'.join(sur.split('/')[:-1]).replace('Mobius/', '')
                value = jres['m2m:sgn']['nev']['rep']['m2m:cin']['con']  # TODO could be a list?

                ngsildentity_id = "urn:ngsi-ld:" + v_thing_name + ':' + cnt_arn.replace('/', ':')
                ngsildentity_cnt_arn = cnt_arn.replace('/', ':')

                ngsiLdEntity1 = {"id": ngsildentity_id,
                                 "type": vtype,
                                 ngsildentity_cnt_arn: {"type": "Property", "value": value}}

                context_vThing.update([ngsiLdEntity1])
                message = {"data": [ngsiLdEntity1], "meta": {"vThingID": v_thing_ID}}
                print("topic name: " + v_thing_topic + '/' + v_thing_data_suffix + " ,message: " + json.dumps(message))
                mqtt_data_client.publish(v_thing_topic + '/' + v_thing_data_suffix,
                                         json.dumps(message))  # publish received data to data topic by using neutral format
                return 'OK', 201

            else:
                print("Bad notification format")
                return 'Bad notification format', 401

        except Exception as err:
            print("Bad notification format, error:", err)
            return 'Bad notification format', 401


class mqttDataThread(Thread):
    # mqtt client used for sending data
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
        message = {"command": "getContextResponse", "data": context_vThing.get_all(), "meta": {"vThingID": v_thing_ID}}
        mqtt_control_client.publish(v_silo_prefix + "/" + silo_id + "/" + in_control_suffix, json.dumps(message))

    def send_destroy_v_thing_message(self):
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
        clean()
        self.send_destroy_v_thing_message()
        self.send_destroy_thing_visor_ack_message()
        print("Shutdown completed")

    # handler for mqtt control topics
    def __init__(self):
        Thread.__init__(self)

    def on_message_in_control_vThing(self, mosq, obj, msg):
        payload = msg.payload.decode("utf-8", "ignore")
        print(msg.topic + " " + str(payload))
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
        mqtt_control_client.publish(tv_control_prefix + "/" + thing_visor_ID + "/" + out_control_suffix,
                                    json.dumps(v_thing_message))

        # Add message callbacks that will only trigger on a specific subscription match
        mqtt_control_client.message_callback_add(v_thing_topic + "/" + in_control_suffix,
                                                 self.on_message_in_control_vThing)
        mqtt_control_client.message_callback_add(tv_control_prefix + "/" + thing_visor_ID + "/" + in_control_suffix,
                                                 self.on_message_in_control_TV)
        mqtt_control_client.subscribe(v_thing_topic + '/' + in_control_suffix)
        mqtt_control_client.subscribe(tv_control_prefix + "/" + thing_visor_ID + "/" + in_control_suffix)
        mqtt_control_client.loop_forever()
        print("Thread '" + self.name + "' terminated")


def add_mobius_sub():
    global cnt_arns, v_thing_ID, notification_URI, CSE_url, origin, sub_rn
    for cnt_arn in cnt_arns:
        print("Mobius subscription" + " " + origin + " " + str(notification_URI) + " " + cnt_arn + " " + CSE_url)
        status, sub = F4Im2m.sub_create(sub_rn, origin, notification_URI, "Mobius/" + cnt_arn, CSE_url)
        if status == 404:
            print(sub)
            sys.exit()
        time.sleep(0.05)


def clean():
    global origin, cnt_arns, CSE_url, sub_rn
    # subscriptions delete
    for cnt_arn in cnt_arns:
        subUri = "Mobius/" + cnt_arn + "/" + sub_rn
        print("deleting subscriptions, wait.....")
        F4Im2m.sub_delete(subUri, origin, CSE_url)
        time.sleep(0.05)


# main
if __name__ == '__main__':

    # For debugging purposes
    # os.environ = {'MQTTDataBrokerIP': '172.17.0.1',
    #                 'MQTTDataBrokerPort': 1883,
    #                 'MQTTControlBrokerIP': '172.17.0.1',
    #                 'MQTTControlBrokerPort': 1883,
    #                 'params': {
    #                            # 'CSEurl': 'https://fed4iot.eglobalmark.com',
    #                            'CSEurl': 'http://172.17.0.1:32793',
    #                            'origin': 'Superman',
    #                            # 'cntArns': 'weather:Tokyo_temp/Tokyo:temp/thermometer',
    #                            'cntArns': ['weather:Tokyo_temp/Tokyo:temp/thermometer'],
    #                            # 'cntArns': ["Abbas123456/humidity/value","Abbas123456/temperature/value"],
    #                            'vThingName': 'mobius_weather/Tokyo_temp',
    #                            # 'vThingName': 'EGM-Abbas123456',
    #                            'vThingDescription': 'OneM2M temp'
    #                             },
    #                 'thingVisorID': 'test-oneM2M',
    #                 'systemDatabaseIP': '172.17.0.1',
    #                 'systemDatabasePort': 32768}

    MAX_RETRY = 3

    thing_visor_ID = os.environ["thingVisorID"]

    # Mqtt settings
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
    tv_entry = db[thing_visor_collection].find_one({"thingVisorID": thing_visor_ID})

    valid_tv_entry = False
    for x in range(MAX_RETRY):
        if tv_entry is not None:
            valid_tv_entry = True
            break
        time.sleep(3)

    if not valid_tv_entry:
        print("Error: ThingVisor entry not found for thing_visor_ID:", thing_visor_ID)
        exit(1)

    try:
        # import paramenters from DB
        MQTT_data_broker_IP = tv_entry["MQTTDataBroker"]["ip"]
        MQTT_data_broker_port = int(tv_entry["MQTTDataBroker"]["port"])
        MQTT_control_broker_IP = tv_entry["MQTTControlBroker"]["ip"]
        MQTT_control_broker_port = int(tv_entry["MQTTControlBroker"]["port"])

        params = tv_entry["params"]

        CSE_url = params['CSEurl']
        cnt_arns = params['cntArns']  # array of source container absolute resource names
        v_thing_name = params["vThingName"]
        v_thing_label = v_thing_name
        v_thing_description = params["vThingDescription"]
        origin = params["origin"]


    except json.decoder.JSONDecodeError:
        print("error on params (JSON) decoding" + "\n")
        exit(1)
    except Exception as e:
        print("Error: Parameters not found in tv_entry", e)
        exit(1)



    # parameters = os.environ["params"]
    # if parameters:
    #     try:
    #         params = json.loads(parameters)
    #         CSE_url = params['CSEurl']
    #         cnt_arns = params['cntArns']  # array of source container absolute resource names
    #         v_thing_name = params["vThingName"]
    #         v_thing_label = v_thing_name
    #         v_thing_description = params["vThingDescription"]
    #         origin = params["origin"]
    #     except json.decoder.JSONDecodeError:
    #         # TODO manage exception
    #         print("error on params (JSON) decoding")
    #         os._exit(1)
    #     except KeyError:
    #         print(Exception.with_traceback())
    #         os._exit(1)

    v_thing_ID = thing_visor_ID + "/" + v_thing_name
    v_thing = {"label": v_thing_label,
               "id": v_thing_ID,
               "description": v_thing_description}

    # MQTT_data_broker_IP = os.environ["MQTTDataBrokerIP"]
    # MQTT_data_broker_port = int(os.environ["MQTTDataBrokerPort"])
    # MQTT_control_broker_IP = os.environ["MQTTControlBrokerIP"]
    # MQTT_control_broker_port = int(os.environ["MQTTControlBrokerPort"])

    sub_rn = v_thing_ID.replace("/",":") + "_subF4I"
    vtype = ""

    # Context is a "map" of current virtual thing state
    context_vThing = Context()
    # mapping of virtual thing with its context object. Useful in case of multiple virtual things
    contexts = {v_thing_ID: context_vThing}

    # # Mqtt settings
    # tv_control_prefix = "TV"  # prefix name for controller communication topic
    # v_thing_prefix = "vThing"  # prefix name for virtual Thing data and control topics
    # v_thing_data_suffix = "data_out"
    # in_control_suffix = "c_in"
    # out_control_suffix = "c_out"
    # v_silo_prefix = "vSilo"
    #
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

    thread1 = httpThread()  # http server used to receive subscribed data
    thread1.start()

    mqtt_control_thread = mqttControlThread()       # mqtt control thread
    mqtt_control_thread.start()

    mqtt_data_thread = mqttDataThread()             # mqtt data thread
    mqtt_data_thread.start()

    time.sleep(2)
    add_mobius_sub()  # add subscription to container to receive published data
    # thread1.join()
    # thread2.join()
    while True:
        try:
            time.sleep(3)
        except:
            print("KeyboardInterrupt")
            clean()
            time.sleep(1)
            os._exit(1)
