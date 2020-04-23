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

sys.path.insert(0, '/app/PyLib/')
import F4Im2m

# MQTT settings
v_silo_prefix = "vSilo"  # prefix name for virtual IoT System communication topic
v_thing_prefix = "vThing"  # prefix name for virtual Thing data and control topics
in_control_suffix = "c_in"
out_control_suffix = "c_out"
v_thing_data_suffix = "data_out"

mqtt_control_client = mqtt.Client()
mqtt_data_client = mqtt.Client()

MOBIUS_IP = "127.0.0.1"
MOBIUS_PORT = 7579

# -*- coding: utf-8 -*-


class mqtt_data_thread(Thread):
    def __init__(self):
        Thread.__init__(self)

    def run(self):
        mqtt_data_client.connect(virIoT_mqtt_data_broker_IP, virIoT_mqtt_data_broker_port, 10)
        mqtt_data_client.loop_forever()
        print("Thread mqtt_data stopped")


class mqtt_control_thread(Thread):
    def __init__(self):
        Thread.__init__(self)

    def run(self):
        global mqtt_control_client
        mqtt_control_client.connect(virIoT_mqtt_control_broker_IP, virIoT_mqtt_control_broker_port, 10)
        # Add message callbacks that will only trigger on a specific subscription match
        mqtt_control_client.message_callback_add(v_silo_prefix + "/" + v_silo_id + "/" + in_control_suffix,
                                                 on_in_control_msg)
        mqtt_control_client.subscribe(v_silo_prefix + "/" + v_silo_id + "/" + in_control_suffix)
        print("Thread mqtt_control started")
        mqtt_control_client.loop_forever()
        print("Thread mqtt_control terminated")


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
            on_message_delete_vThing(jres)
            return "deleting vThing"
        elif commandType == "destroyVSilo":
            on_message_destroy_v_silo(jres)
            return "destroying vSilo"
        elif commandType == "getContextResponse":
            del jres["command"]
            on_vThing_data(mosq, obj, json.dumps(jres))
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


def on_message_delete_vThing(jres):
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
        on_message_delete_vThing(msg)
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


def handler(signal, frame):
    sys.exit()


signal.signal(signal.SIGINT, handler)


# ############ Mobius Functions ############
application_entities = []           # list of running application entities
containers = []                     # list of running containers
mobius_initial_status = {}

containers_uri = set()              # set of container uri
application_entities_rn = set()     # set of ae resource names


def init_Mobius():
    global CSEurl, origin, usecsebase, acp_ri, mobius_initial_status, containers
    # Mobius settings
    CSEurl = "http://" + MOBIUS_IP + ":"+str(MOBIUS_PORT)
    origin = "S"
    usecsebase = 'Mobius'

    acp_list = []
    ae_list = []
    cnt_list = []
    # retrieve initial mobius broker status
    mobius_initial_status_str = F4Im2m.cse_inspect(origin=origin, CSEurl=CSEurl)
    mobius_initial_status = json.loads(mobius_initial_status_str)
    if 'm2m:rsp' in mobius_initial_status:
        if 'm2m:acp' in mobius_initial_status['m2m:rsp']:
            acp_list = mobius_initial_status['m2m:rsp']['m2m:acp']      # existing policies
        if 'm2m:ae' in mobius_initial_status['m2m:rsp']:
            ae_list = mobius_initial_status['m2m:rsp']['m2m:ae']        # existing application entities
        if 'm2m:cnt' in mobius_initial_status['m2m:rsp']:
            cnt_list = mobius_initial_status['m2m:rsp']['m2m:cnt']      # existing containers

    if len(acp_list) == 0:
        # create single Policy
        rn_acp = "policy1"
        pv = {"acr": [{"acor": [tenant_id], "acop": "3"}, {"acor": [origin], "acop": "63"}]}
        pvs = {"acr": [{"acor": ["admin"], "acop": "63"}]}
        status, acp = F4Im2m.acp_create(CSEurl, origin, rn_acp, pv, pvs)
        print("\nCreate ACP: ", rn_acp)
        acp_ri = acp['ri']
    else:
        acp_ri = acp_list[0]['ri']
    for ae in ae_list:
        application_entities.append({'rn': ae['rn'], 'pi': ae['pi'], 'ri': ae['ri']})
        application_entities_rn.add(ae['rn'])
    for cnt in cnt_list:
        containers.append({'rn': cnt['rn'], 'pi': cnt['pi'], 'ri': cnt['ri']})
    top_containers = []
    sub_containers = []
    for cnt in containers:
        is_top_cnt = False
        pi = cnt['pi']
        for ae in application_entities:
            if ae['ri'] == pi:
                uri = usecsebase + '/' + ae['rn'] + '/' + cnt['rn']
                top_containers.append({"cnt": cnt, "uri": uri})
                is_top_cnt = True
                break
        if not is_top_cnt:
            sub_containers.append(cnt)

    for sub_cnt in sub_containers:
        for top_cnt in top_containers:
            if sub_cnt['pi'] == top_cnt['cnt']['ri']:
                uri = top_cnt['uri'] + '/' + sub_cnt['rn']
                containers_uri.add(uri)
                break
    restore_virtual_things()


def create_vThing_Mobius(jres):
    try:
        v_thing_id = jres['vThingID']
        # create AE
        ae_rn = v_thing_id.replace("/", ":")
        if ae_rn not in application_entities_rn:         # control if ae already exists in mobius broker
            gapi = "v1"
            grr = False
            gpoa = []
            glbl = []
            gstatus, gae = F4Im2m.ae_create(ae_rn, origin, gapi, grr, gpoa, glbl, CSEurl)
            # print(gae)
            # bind AE with ACP
            acpi = acp_ri
            ae_rn = gae['rn']
            status, ae = F4Im2m.ae_acp_update(CSEurl, origin, ae_rn, acpi)
            print("\nAE created:", ae_rn)
            # print(ae)
            application_entities_rn.add(ae_rn)
            application_entities.append({'rn': gae['rn'], 'ri': gae['ri'], 'pi': gae['pi']})
        else:
            print("ae " + ae_rn + " already exists")
        return True
    except Exception as ex:
        traceback.print_exc()
        return False


def delete_vThing_Mobius(jres):
    try:
        v_thing_id = jres['vThingID']
        # removing tenant application entity, thereby all container, cin, subscriptions
        ae_rn = v_thing_id.replace('/', ':')
        status, response = F4Im2m.ae_delete(usecsebase + "/" + ae_rn, origin, CSEurl)
        ae_to_remove = None
        if status == 200:
            application_entities_rn.remove(ae_rn)
            for ae in application_entities:
                if ae_rn == ae['rn']:
                    ae_to_remove = ae
                    break
            if ae_to_remove is not None:
                application_entities.remove(ae_to_remove)
            cnt_to_remove_list = []
            for cnt in containers:
                if str(cnt).startswith(usecsebase + "/" + ae_rn):
                    cnt_to_remove_list.append(cnt)
            for cnt_to_remove in cnt_to_remove_list:
                print("removing " + cnt_to_remove + " from containers_rn list")
                containers.remove(cnt_to_remove)
            return True
        else:
            return False
    except Exception as ex:
        traceback.print_exc()
        return False


def on_vThing_data_Mobius(jmessage):

    # NGSI-LD --> oneM2M mapping (D2.2)
    v_thing_id = jmessage['meta']['vThingID']
    ae_rn = v_thing_id.replace("/", ":")
    ae_uri = usecsebase + "/" + ae_rn

    data = jmessage['data']  # Array of NGSI-LD entities

    for entity in data:
        id = entity['id']
        id = id.replace("urn:ngsi-ld:","")
        label = [entity['type']]
        main_container_uri = ae_uri + "/" + id
        # print the keys and values
        for key in entity:
            if key not in ["id", "type"]:
                sub_container_uri = main_container_uri + "/" + key
                value = entity[key]
                if sub_container_uri in containers_uri:
                    res = F4Im2m.create_cin(sub_container_uri, origin, str(value), CSEurl)
                # print("res: " + str(res))
                else:
                    # attempt 1 - try to create sub container, if no error then insert
                    mni = 10  # number of content instances in the container
                    res1 = F4Im2m.container_create(key, origin, main_container_uri, mni, [], CSEurl)
                    # print("res1: " + str(res1))
                    time.sleep(0.1)
                    if res1[0] != 201:
                        # attempt 2 - try to create main and sub containers, if no error then insert
                        res2 = F4Im2m.container_create(id, origin, ae_uri, mni, label, CSEurl)
                        time.sleep(0.1)
                        res3 = F4Im2m.container_create(key, origin, main_container_uri, mni, [], CSEurl)
                        time.sleep(0.1)
                        if res2[0] != 201 or res3[0] != 201:
                            print("error, res2: " + str(res2) + " res3: " + str(res3))
                            print("content instance not inserted")
                            continue
                        else:
                            containers_uri.add(sub_container_uri)
                    else:
                        containers_uri.add(sub_container_uri)
                    res4 = F4Im2m.create_cin(sub_container_uri, origin, str(value), CSEurl)
                    if res4[0] != 201:
                        print("error, res4: " + str(res4) + "content instance not inserted")
                        continue
    return 'OK'


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

    tenant_id = os.environ["tenantID"]
    flavourParams = os.environ["flavourParams"]     # in this flavour, param is the silo type (Raw, Mobius, FiWare)
    v_silo_id = os.environ["vSiloID"]
    virIoT_mqtt_data_broker_IP = os.environ["MQTTDataBrokerIP"]
    virIoT_mqtt_data_broker_port = int(os.environ["MQTTDataBrokerPort"])
    virIoT_mqtt_control_broker_IP = os.environ["MQTTControlBrokerIP"]
    virIoT_mqtt_control_broker_port = int(os.environ["MQTTControlBrokerPort"])
    db_IP = os.environ['systemDatabaseIP']  # IP address of system database
    db_port = os.environ['systemDatabasePort']  # port of system database
    print("starting silo controller")

    initEnv = init_Mobius
    delete_vThing_on_Broker = delete_vThing_Mobius
    create_vThing_on_Broker = create_vThing_Mobius
    on_vThing_data_on_broker = on_vThing_data_Mobius

    # Mongodb settings
    db_name = "viriotDB"  # name of system database
    v_thing_collection = "vThingC"

    silo_broker_thread = broker_thread()
    silo_broker_thread.start()
    virIoT_mqtt_data_thread = mqtt_data_thread()
    virIoT_mqtt_data_thread.start()
    virIoT_mqtt_control_thread = mqtt_control_thread()
    virIoT_mqtt_control_thread.start()
