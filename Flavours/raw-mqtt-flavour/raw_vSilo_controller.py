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

# Fed4IoT virtual Silo controller  for oneM2M and Raw (mqtt), to be possibly extended for FiWare

import os
import sys
import time
import signal
import traceback
import paho.mqtt.client as mqtt
import json
from threading import Thread
from pymongo import MongoClient
from bson.json_util import dumps

# MQTT settings
v_silo_prefix = "vSilo"  # prefix name for virtual IoT System communication topic
v_thing_prefix = "vThing"  # prefix name for virtual Thing data and control topics
v_thing_data_suffix = "data_out"
in_control_suffix = "c_in"
out_control_suffix = "c_out"

mqtt_control_client = mqtt.Client()
mqtt_data_client = mqtt.Client()


# -*- coding: utf-8 -*-


class MqttDataThread(Thread):
    def __init__(self):
        Thread.__init__(self)

    def run(self):
        mqtt_data_client.connect(virIoT_mqtt_data_broker_IP, virIoT_mqtt_data_broker_port, 10)
        print("Thread mqtt_data started")
        mqtt_data_client.loop_forever()
        print("Thread mqtt_data terminated")


class MqttControlThread(Thread):
    def __init__(self):
        Thread.__init__(self)

    def run(self):
        global mqtt_control_client
        mqtt_control_client.connect(virIoT_mqtt_control_broker_IP, virIoT_mqtt_control_broker_port, 10)
        # Add message callbacks that will only trigger on a specific subscription match
        mqtt_control_client.message_callback_add(v_silo_prefix + "/" + v_silo_id + "/" + in_control_suffix,
                                                 on_in_control_msg)
        mqtt_control_client.subscribe(v_silo_prefix + "/" + v_silo_id + "/" + in_control_suffix)
        mqtt_control_client.loop_forever()
        print("Thread mqtt_control started")


class broker_thread(Thread):
    def __init__(self):
        Thread.__init__(self)

    def run(self):
        initEnv()
        print("Thread broker started")


# topic messages
def on_in_control_msg(mosq, obj, msg):
    payload = msg.payload.decode("utf-8", "ignore")
    print(msg.topic + " " + str(payload))
    jres = json.loads(payload.replace("\'", "\""))
    try:
        commandType = jres["command"]
        if commandType == "addVThing":
            on_message_add_vThing(jres)
            return "creating vThing"
        elif commandType == "deleteVThing":
            on_message_delete_thing(jres)
            return "deleting vThing"
        elif commandType == "destroyVSilo":
            on_message_destroy_v_silo(jres)
            return "destroying vSilo"
        elif commandType == "getContextResponse":
            del jres["command"]
            on_vThing_data(mosq, obj, str(jres))
            return "received context response"
        else:
            return "invalid command"
    except Exception as ex:
        traceback.print_exc()
        return 'invalid command'


def on_message_add_vThing(jres):
    # print("on_message_add_vThing")
    try:
        v_thing_id = jres['vThingID']
        res = create_vThing_on_Broker(jres)
        if res:
            print("subscribing to vThing topics: ")
            # add subscription for virtual Thing data topic (on mqtt data client)
            print(v_thing_prefix + '/' + v_thing_id + '/' + v_thing_data_suffix)
            mqtt_data_client.subscribe(v_thing_prefix + '/' + v_thing_id + '/' + v_thing_data_suffix)
            mqtt_data_client.message_callback_add(v_thing_prefix + '/' + v_thing_id + '/' + v_thing_data_suffix,
                                                  on_vThing_data)
            # add subscription for virtual Thing control topic (on mqtt control client)
            print(v_thing_prefix + '/' + v_thing_id + '/' + out_control_suffix)
            mqtt_control_client.subscribe(v_thing_prefix + '/' + v_thing_id + '/' + out_control_suffix)
            mqtt_control_client.message_callback_add(v_thing_prefix + '/' + v_thing_id + '/' + out_control_suffix,
                                                     on_vThing_out_control)
            # retrieve last context for the virtual thing from the thing visor
            fetch_last_context(v_thing_id)
            return 'OK'
        else:
            return 'Creatiion fails'
    except Exception as ex:
        traceback.print_exc()
        return 'ERROR'


def on_message_delete_thing(jres):
    # print("on_message_delete_vThing")
    try:
        v_thing_id = jres['vThingID']
        # removing mqtt subscriptions and callbacks
        mqtt_data_client.message_callback_remove(v_thing_prefix + '/' + v_thing_id + '/' + v_thing_data_suffix)
        mqtt_data_client.unsubscribe(v_thing_prefix + '/' + v_thing_id + '/' + v_thing_data_suffix)

        mqtt_control_client.message_callback_remove(v_thing_prefix + '/' + v_thing_id + '/out_control')
        mqtt_control_client.unsubscribe(v_thing_prefix + '/' + v_thing_id + '/out_control')
        delete_vThing_on_Broker(jres)

    except Exception:
        traceback.print_exc()
        return 'ERROR'


def on_vThing_data(mosq, obj, msg):
    try:
        if isinstance(msg, str):
            jres = json.loads(msg.replace("\'", "\""))
        else:
            payload = msg.payload.decode("utf-8", "ignore")
            jres = json.loads(payload.replace("\'", "\""))
        print("enter on_vThing_data, msg.payload: " + str(jres))
        on_vThing_data_on_broker(jres)
    except Exception as ex:
        traceback.print_exc()
        print('ERROR in on_vThing_data')
        return 'ERROR'
    return 'OK'


def on_vThing_out_control(mosq, obj, msg):
    print("on_vThing_out_control")
    payload = msg.payload.decode("utf-8", "ignore")
    jres = json.loads(payload.replace("\'", "\""))
    if jres["command"] == "deleteVThing":
        msg = {"vThingID": jres["vThingID"]}
        on_message_delete_thing(msg)
    else:
        # TODO manage others commands
        return 'command not managed'
    return 'OK'


def send_destroy_v_silo_ack_message():
    msg = {"command": "destroyVSiloAck", "vSiloID": v_silo_id}
    mqtt_control_client.publish(v_silo_prefix + "/" + v_silo_id + "/" + out_control_suffix, str(msg).replace("\'", "\""))
    return


def on_message_destroy_v_silo(jres):
    global mqtt_control_client
    send_destroy_v_silo_ack_message()
    mqtt_control_client.disconnect()

    print("Shutdown completed")


def fetch_last_context(v_thing_id):
    message = {"command": "getContextRequest", "vSiloID": v_silo_id, "vThingID": v_thing_id}
    mqtt_control_client.publish(v_thing_prefix + "/" + v_thing_id + "/" + in_control_suffix, str(message).replace("\'", "\""))


def handler(signal, frame):
    sys.exit()


signal.signal(signal.SIGINT, handler)


def init_Raw():
    global tenant_mqttc
    tenant_mqttc = mqtt.Client()
    tenant_mqttc.connect("127.0.0.1")
    restore_virtual_things()
    tenant_mqttc.loop_forever()
    return True


def create_vThing_Raw(jres):
    # do nothing, virtual thing topics already subscribed
    return True


def delete_vThing_Raw(jres):
    # do nothing, virtual thing topics already unsubscribed
    return True


def on_vThing_data_Raw(jmessage):
    global tenant_mqttc
    v_thing_id = jmessage['meta']['vThingID']
    mqtt_msg = jmessage
    tenant_mqttc.publish(tenant_id + '/' + v_thing_id, str(mqtt_msg).replace("\'", "\""))
    return 'OK'


def restore_virtual_things():
    # Retrieve from system db the list of virtual thing in use and restore them
    # needed in case of silo controller restart
    db_client = MongoClient('mongodb://' + db_IP + ':' + str(db_port) + '/')
    db = db_client[db_name]
    connected_v_things = json.loads(
        dumps(db[v_thing_collection].find({"vSiloID": v_silo_id}, {"vThingID": 1, "_id": 0})))
    if len(connected_v_things) > 0:
        for vThing in connected_v_things:
            if "vThingID" in vThing:
                print("restoring virtual thing with ID: " + vThing['vThingID'])
                on_message_add_vThing(vThing)


if __name__ == '__main__':

    # -------------- DEBUG PARAMETERS --------------
    # tenant_id = "tenant1"
    # flavourParams = []
    # v_silo_id = "tenant1_Silo2"
    # virIoT_mqtt_data_broker_IP = "127.0.0.1"
    # virIoT_mqtt_data_broker_port = 1883
    # virIoT_mqtt_control_broker_IP = "127.0.0.1"
    # virIoT_mqtt_control_broker_port = 1883
    # db_IP = "172.17.0.2"
    # db_port = 27017

    MAX_RETRY = 3
    v_silo_id = os.environ["vSiloID"]
    db_IP = os.environ['systemDatabaseIP']  # IP address of system database
    db_port = os.environ['systemDatabasePort']  # port of system database

    # Mongodb settings
    time.sleep(1.5)  # wait before query the system database
    db_name = "viriotDB"  # name of system database
    v_thing_collection = "vThingC"
    v_silo_collection = "vSiloC"
    db_client = MongoClient('mongodb://' + db_IP + ':' + str(db_port) + '/')
    db = db_client[db_name]
    silo_entry = db[v_silo_collection].find_one({"vSiloID": v_silo_id})

    ##############################
    ##############################
    valid_silo_entry = False
    for x in range(MAX_RETRY):
        if silo_entry is not None:
            valid_silo_entry = True
            break
        time.sleep(3)

    if not valid_silo_entry:
        print("Error: Virtual Silo entry not found for v_silo_id:", v_silo_id)
        exit()

    try:
        # import paramenters from DB
        tenant_id = silo_entry["tenantID"]
        flavourParams = silo_entry["flavourParams"]  # in this flavour, param is the silo type (Raw, Mobius, FiWare)

        virIoT_mqtt_data_broker_IP = silo_entry["MQTTDataBroker"]["ip"]
        virIoT_mqtt_data_broker_port = int(silo_entry["MQTTDataBroker"]["port"])
        virIoT_mqtt_control_broker_IP = silo_entry["MQTTControlBroker"]["ip"]
        virIoT_mqtt_control_broker_port = int(silo_entry["MQTTControlBroker"]["port"])


    except Exception as e:
        print("Error: Parameters not found in silo_entry", e)
        exit()

    ##############################
    ##############################

    # tenant_id = os.environ["tenantID"]
    # flavourParams = os.environ["flavourParams"]  # in this flavour, param is the silo type (Raw, Mobius, FiWare)
    # v_silo_id = os.environ["vSiloID"]
    # virIoT_mqtt_data_broker_IP = os.environ["MQTTDataBrokerIP"]
    # virIoT_mqtt_data_broker_port = int(os.environ["MQTTDataBrokerPort"])
    # virIoT_mqtt_control_broker_IP = os.environ["MQTTControlBrokerIP"]
    # virIoT_mqtt_control_broker_port = int(os.environ["MQTTControlBrokerPort"])
    # db_IP = os.environ['systemDatabaseIP']  # IP address of system database
    # db_port = os.environ['systemDatabasePort']  # port of system database
    db_client.close()  # Close DB connection
    print("starting silo controller")

    initEnv = init_Raw
    delete_vThing_on_Broker = delete_vThing_Raw
    create_vThing_on_Broker = create_vThing_Raw
    on_vThing_data_on_broker = on_vThing_data_Raw

    # Mongodb settings
    db_name = "viriotDB"  # name of system database
    v_thing_collection = "vThingC"

    silo_broker_thread = broker_thread()
    silo_broker_thread.start()
    virIoT_mqtt_data_thread = MqttDataThread()
    virIoT_mqtt_data_thread.start()
    virIoT_mqtt_control_thread = MqttControlThread()
    virIoT_mqtt_control_thread.start()
