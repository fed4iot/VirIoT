#!/usr/bin/python3

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

# Fed4IoT virtual Silo controller for oneM2M internal broker



from bson.json_util import dumps
from pymongo import MongoClient
from threading import Thread
import json
import paho.mqtt.client as mqtt
import traceback
import signal
import time

import os
import sys

sys.path.insert(0, '/app/PyLib/')
import F4Im2m

# -*- coding: utf-8 -*-

# in control messages messages


def on_in_control_msg(mosq, obj, msg):
    payload = msg.payload.decode("utf-8", "ignore")
    print("In control message received by vSilo "+payload)
    try:
        jres = json.loads(payload.replace("\'", "\""))
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
    try:
        v_thing_id = jres['vThingID']
        res = on_add_vThing_on_Broker(jres)
        if res:
            # add subscription for virtual Thing data topic (on mqtt data client)
            mqtt_virIoT_data_client.subscribe(
                v_thing_prefix + '/' + v_thing_id + '/' + data_out_suffix)
            mqtt_virIoT_data_client.message_callback_add(v_thing_prefix + '/' + v_thing_id + '/' + data_out_suffix,
                                                         on_vThing_data)
            # add subscription for virtual Thing control topic (on mqtt control client)
            mqtt_virIoT_control_client.subscribe(
                v_thing_prefix + '/' + v_thing_id + '/' + control_out_suffix)
            mqtt_virIoT_control_client.message_callback_add(v_thing_prefix + '/' + v_thing_id + '/' + control_out_suffix,
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
    try:
        v_thing_id = jres['vThingID']
        # removing mqtt subscriptions and callbacks
        mqtt_virIoT_data_client.message_callback_remove(
            v_thing_prefix + '/' + v_thing_id + '/' + data_out_suffix)
        mqtt_virIoT_data_client.unsubscribe(
            v_thing_prefix + '/' + v_thing_id + '/' + data_out_suffix)

        mqtt_virIoT_control_client.message_callback_remove(
            v_thing_prefix + '/' + v_thing_id + '/out_control')
        mqtt_virIoT_control_client.unsubscribe(
            v_thing_prefix + '/' + v_thing_id + '/out_control')
        on_delete_vThing_on_Broker(jres)

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
        on_vThing_data_on_Broker(jres)
    except Exception as ex:
        traceback.print_exc()
        print('ERROR in on_vThing_data')
        return 'ERROR'

    return 'OK'


def on_vThing_out_control(mosq, obj, msg):
    payload = msg.payload.decode("utf-8", "ignore")
    print("Out control message received by vThing "+payload)
    try:
        jres = json.loads(payload.replace("\'", "\""))
        if jres["command"] == "deleteVThing":
            msg = {"vThingID": jres["vThingID"]}
            on_message_delete_vThing(msg)
        else:
            # TODO manage others commands
            return 'command not managed'
        return 'OK'
    except Exception as ex:
        traceback.print_exc()
        print('ERROR in on_vThing_out_control')
        return 'ERROR'


def send_destroy_v_silo_ack_message():
    msg = {"command": "destroyVSiloAck", "vSiloID": v_silo_id}
    mqtt_virIoT_control_client.publish(
        v_silo_prefix + "/" + v_silo_id + "/" + control_out_suffix, json.dumps(msg))
    return


def on_message_destroy_v_silo(jres):
    global mqtt_virIoT_control_client
    send_destroy_v_silo_ack_message()
    mqtt_virIoT_control_client.disconnect()
    print("Shutdown completed")


def fetch_last_context(v_thing_id):
    message = {"command": "getContextRequest",
               "vSiloID": v_silo_id, "vThingID": v_thing_id}
    mqtt_virIoT_control_client.publish(v_thing_prefix + "/" + v_thing_id +
                                       "/" + control_in_suffix, json.dumps(message))


def restore_virtual_things():
    # Retrieve from system db the list of virtual thing in use and restore them
    # needed in case of silo controller restart
    try:
        db_client = MongoClient('mongodb://' + db_IP +
                                ':' + str(db_port) + '/')
        db = db_client[db_name]
        connected_v_things = json.loads(
            dumps(db[v_thing_collection].find({"vSiloID": v_silo_id}, {"vThingID": 1, "_id": 0})))
        if len(connected_v_things) > 0:
            for vThing in connected_v_things:
                if "vThingID" in vThing:
                    print("Restoring virtual thing with ID: " +
                          vThing['vThingID'])
                    # find vThing type, if any
                    v_thing_id = vThing['vThingID']
                    vthings_of_tv = db[thing_visor_collection].find_one(
                        {"vThings.id": v_thing_id})['vThings']
                    vThing['vThingType'] = ""
                    for vt in vthings_of_tv:
                        if vt['id'] == v_thing_id and 'type' in vt:
                            vThing['vThingType'] = vt['type']
                        break
                    on_message_add_vThing(vThing)
    except Exception as ex:
        traceback.print_exc()
        print('ERROR in restore_virtual_things')
        return 'ERROR'


def send_command_out(cmd_LD_ID, cmd_LD_Type, cmd_name, cmd_value, vThingID):

    ngsiLdEntity = {"id": cmd_LD_ID, "type": cmd_LD_Type,
                    cmd_name: {"type": "Property", "value": cmd_value}}
    data = [ngsiLdEntity]
    topic = "vThing/"+vThingID+"/data_in"
    # publish changed status
    message = {"data": data, "meta": {
        "vSiloID": v_silo_id}}  # neutral-format
    publish_on_virIoT(message, topic)
    return


def publish_on_virIoT(message, out_topic):
    msg = json.dumps(message)
    print("Message sent on "+out_topic + "\n" + msg+"\n")
    # publish data to out_topic
    mqtt_virIoT_data_client.publish(out_topic, msg)


def handler(signal, frame):
    sys.exit()


signal.signal(signal.SIGINT, handler)


# ############ Mobius Functions ############
# set used to store uri of container already created,
# it is necessary because content-instance are  inserted through MQTT without any exception
containers_uri_set = set()

# dictinary binding entity with type,
# it is useful to accelerate the NGSI-LD command building, otherwise a Mobius lookup is necessary
id_LD_type_dict = dict()


def init_Mobius():
    global CSEurl, origin, usecsebase, acp_ri, mobius_initial_status

    # Mobius settings

    CSEurl = "http://" + BROKER_IP + ":"+str(BROKER_HTTP_PORT)
    origin = "S"
    usecsebase = 'Mobius'
    acp_list = []

    # retrieve initial mobius broker status
    mobius_initial_status_str = F4Im2m.cse_inspect(
        origin=origin, CSEurl=CSEurl)
    mobius_initial_status = json.loads(mobius_initial_status_str)

    # Access Control Policy setup
    if 'm2m:rsp' in mobius_initial_status:
        if 'm2m:acp' in mobius_initial_status['m2m:rsp']:
            # existing policies
            acp_list = mobius_initial_status['m2m:rsp']['m2m:acp']
            acp_ri = acp_list[0]['ri']
        else:
            # create single Policy
            rn_acp = "policy1"
            pv = {"acr": [{"acor": [tenant_id], "acop": "3"},
                          {"acor": [origin], "acop": "63"}]}
            pvs = {"acr": [{"acor": ["admin"], "acop": "63"}]}
            status, acp = F4Im2m.acp_create(CSEurl, origin, rn_acp, pv, pvs)
            acp_ri = acp['ri']


def on_add_vThing_Mobius(jres):
    try:
        v_thing_id = jres['vThingID']
        # check if AE already exist on the broker, otherwise create it
        # neutral-format --> oneM2M binding (D2.2)
        ae_rn = v_thing_id.replace("/", ":")
        status, gae = F4Im2m.entity_get(usecsebase+"/"+ae_rn, origin, CSEurl)
        if status != 200:
            # create AE
            gapi = "v1"
            grr = False
            gpoa = []
            glbl = []
            gstatus, gae = F4Im2m.ae_create(
                ae_rn, origin, gapi, grr, gpoa, glbl, CSEurl)

            # bind AE with ACP
            acpi = acp_ri
            ae_rn = gae['rn']
            status, ae = F4Im2m.ae_acp_update(CSEurl, origin, ae_rn, acpi)
        return True
    except Exception as ex:
        traceback.print_exc()
        return False


def on_delete_vThing_Mobius(jres):
    try:
        v_thing_id = jres['vThingID']
        # removing tenant application entity, thereby all container, cin, subscriptions
        ae_rn = v_thing_id.replace('/', ':')
        status, response = F4Im2m.ae_delete(
            usecsebase + "/" + ae_rn, origin, CSEurl)
        if status == 200 or status == 201:
            # remove containers of the deleted vThing from the local container_uri local set
            # remove id from type map

            # identification phase
            cnt_uri_to_remove_set = set()
            id_LD_to_remove_set = set()
            for cnt in containers_uri_set:
                if str(cnt).startswith(usecsebase + "/" + ae_rn):
                    cnt_uri_to_remove_set.add(cnt)
                    # cnt_uri Mobius/<vThingID>/<id_LD>/<Property_name>
                    id_LD = str(cnt).split("/")[2]
                    id_LD_to_remove_set.add(id_LD)

            # cleaning phase
            containers_uri_set.difference_update(cnt_uri_to_remove_set)
            for id_LD in id_LD_to_remove_set:
                if id_LD in id_LD_type_dict:
                    del id_LD_type_dict[id_LD]

            return True
        else:
            return False
    except Exception as ex:
        traceback.print_exc()
        return False


def on_vThing_data_Mobius(jmessage):

    # neutral-format (data:<NGSI-LD>, meta:<JSON>) --> oneM2M mapping (D2.2)
    v_thing_id = jmessage['meta']['vThingID']
    ae_rn = v_thing_id.replace("/", ":")
    ae_uri = usecsebase + "/" + ae_rn
    # Array of NGSI-LD entities contained in the neutral-format message
    data = jmessage['data']

    for entity in data:
        id = entity['id']
        label = [entity['type']]

        # remove urn:ngls-ld for oneM2M readability
        if id.startswith("urn:ngsi-ld:"):
            main_container_rn = id[len("urn:ngsi-ld:"):]
        else:
            main_container_rn = id

        main_container_uri = ae_uri + "/" + main_container_rn

        # map any ngsi-ld key different from id, type and annotations "@"
        # as sub-container (key name)
        # and content instance (key value)
        for key in entity:
            if (key not in ["id", "type", "commands"]) and (key.startswith("@") == False):

                mni = 1  # number of content instances in the oneM2M container for data
                value = entity[key]  # value to be inserted as content instance
                sub_container_rn = key
                sub_container_uri = main_container_uri + "/" + sub_container_rn

                if sub_container_uri in containers_uri_set:
                    # sub-container already there, insertion of content instance
                    create_cin_mqtt(sub_container_uri, origin,
                                    str(value), usecsebase, ae_rn)
                else:
                    if main_container_uri not in containers_uri_set:
                        # create main-container
                        status_mc, mc = F4Im2m.container_create(
                            main_container_rn, origin, ae_uri, mni, label, CSEurl)
                        containers_uri_set.add(main_container_uri)
                        id_LD_type_dict[id] = entity['type']
                        time.sleep(0.1)
                    # create sub-container
                    status_mc, mc = F4Im2m.container_create(
                        sub_container_rn, origin, main_container_uri, mni, label, CSEurl)
                    containers_uri_set.add(sub_container_uri)
                    time.sleep(0.1)
                    # content instance insertion
                    create_cin_mqtt(sub_container_uri, origin,
                                    str(value), usecsebase, ae_rn)
            elif key == "commands":
                mni = 3
                if main_container_uri not in containers_uri_set:
                    # create main-container
                      # number of content instances in the oneM2M container for command
                    status_mc, mc = F4Im2m.container_create(
                        main_container_rn, origin, ae_uri, mni, label, CSEurl)
                    containers_uri_set.add(main_container_uri)
                    time.sleep(0.1)
                # creates sub-containers for each command
                commands = entity['commands']['value']
                for cmd_name in commands:

                    # sub-container for the command cmd_name
                    sub_container_rn = cmd_name
                    sub_container_uri = main_container_uri + "/" + sub_container_rn
                    if sub_container_uri not in containers_uri_set:
                        status_mc, mc = F4Im2m.container_create(
                            sub_container_rn, origin, main_container_uri, mni, [], CSEurl)
                        containers_uri_set.add(sub_container_uri)
                        # subscribe to this container to receive commands from the vsilo tenant
                        # notification topic actually is /oneM2M/req/Mobius/v_silo_id/json
                        nuri = ["mqtt://127.0.0.1/"+v_silo_id]
                        F4Im2m.sub_create("vSiloCommandSub",
                                          origin, nuri, sub_container_uri, CSEurl)

                    # sub-container for the command status of the cmd_name
                    sub_container_rn = cmd_name+"-status"
                    sub_container_uri = main_container_uri + "/" + sub_container_rn
                    if sub_container_uri not in containers_uri_set:
                        status_mc, mc = F4Im2m.container_create(
                            sub_container_rn, origin, main_container_uri, mni, [], CSEurl)
                        containers_uri_set.add(sub_container_uri)

                    # sub-container for the command result of the cmd_name
                    sub_container_rn = cmd_name+"-result"
                    sub_container_uri = main_container_uri + "/" + sub_container_rn
                    if sub_container_uri not in containers_uri_set:
                        status_mc, mc = F4Im2m.container_create(
                            sub_container_rn, origin, main_container_uri, mni, [], CSEurl)
                        containers_uri_set.add(sub_container_uri)
    return 'OK'


def create_cin_mqtt(container_uri, origin, value, cse, ae):
    topic = "/oneM2M/req/" + ae + "/" + cse + "/json"
    rqp = {"m2m:rqp":
           {"fr": origin,
            "to": container_uri,
            "op": 1,
            "rqi": time.time(),
            "ty": 4,
            "pc":
            {"m2m:cin":
             {"con": value}
             }
            }
           }
    mqtt_broker_client.publish(topic=topic, payload=json.dumps(rqp), qos=1)


def on_commandRequest_Mobius(mosq, obj, msg):
    payload = msg.payload.decode("utf-8", "ignore")

    try:
        jres = json.loads(payload)
        resp_topic = msg.topic.replace("oneM2M/req","oneM2M/resp")
        ae_rn = resp_topic.split("/")[4]
        rqi = jres['rqi']
        response_mqtt_notify(resp_topic,2001, '', origin, rqi, '')  # send Mobius ACK otherwise subscription is deleted

        # e.g. sub_uri = "Mobius/helloWorldActuator:Lamp01/helloWorldActuator:Lamp01/set-luminosity/vSiloCommandSub"
        sub_uri = jres['pc']['m2m:sgn']['sur']
        if "nev" not in jres['pc']['m2m:sgn']:
            return 'OK'
        if "m2m:cin" in jres['pc']['m2m:sgn']['nev']['rep']:
            cmd_value = jres['pc']['m2m:sgn']['nev']['rep']['m2m:cin']['con']
            sub_uri_split = sub_uri.split("/")
            cmd_name = sub_uri_split[-2]
            vThingID = uri2vThingID(sub_uri)
            cmd_LD_ID = "urn:ngsi-ld:"+sub_uri_split[2]
            if cmd_LD_ID in id_LD_type_dict:
                cmd_LD_Type = id_LD_type_dict[cmd_LD_ID]
            else:
                cmd_LD_Type = ""
                print("NGSI-LD type unknowk for command request of entity "+cmd_LD_ID)
            send_command_out(cmd_LD_ID, cmd_LD_Type,
                             cmd_name, cmd_value, vThingID)

    except Exception as ex:
        traceback.print_exc()
    return 'OK'

def response_mqtt_notify (rsp_topic, rsc, to, fr, rqi, inpc):
    global mqtt_broker_client
    rsp_message = {}
    rsp_message['m2m:rsp'] = {}
    rsp_message['m2m:rsp']['rsc'] = rsc
    rsp_message['m2m:rsp']['to'] = rsp_topic
    rsp_message['m2m:rsp']['fr'] = fr
    rsp_message['m2m:rsp']['rqi'] = rqi
    rsp_message['m2m:rsp']['pc'] = inpc
    mqtt_broker_client.publish(topic=rsp_topic, payload=json.dumps(rsp_message),qos=0)

def uri2vThingID(uri):
    # extract vThingID from oneM2M uri e.g. uri = "Mobius/helloWorldActuator:Lamp01/helloWorldActuator:Lamp01/set-color", vThingID "helloWorldActuator/Lamp01"
    vThingID = uri.split("/")[1].replace(":", "/")
    return vThingID


if __name__ == '__main__':

    # -------------- DEBUG PARAMETERS --------------
    # tenant_id = "tenant1"
    # flavourParams = []
    # v_silo_id = "tenant1_Silo1"
    # virIoT_mqtt_data_broker_IP = "127.0.0.1"
    # virIoT_mqtt_data_broker_port = 1883
    # virIoT_mqtt_control_broker_IP = "127.0.0.1"
    # virIoT_mqtt_control_broker_port = 1883
    # db_IP = "172.17.0.2"
    # db_port = 27017
    # MQTT settings

    v_silo_prefix = "vSilo"  # prefix name for virtual IoT System communication topic
    v_thing_prefix = "vThing"  # prefix name for virtual Thing data and control topics
    data_out_suffix = "data_out"
    data_in_suffix = "data_in"
    control_in_suffix = "c_in"
    control_out_suffix = "c_out"

    ########################################################
    ########################################################
    MAX_RETRY = 3
    v_silo_id = os.environ["vSiloID"]
    db_IP = os.environ['systemDatabaseIP']  # IP address of system database
    db_port = os.environ['systemDatabasePort']  # port of system database

    # Mongodb settings
    time.sleep(1.5)  # wait before query the system database
    db_name = "viriotDB"  # name of system database
    v_thing_collection = "vThingC"
    thing_visor_collection = "thingVisorC"
    v_silo_collection = "vSiloC"

    db_client = MongoClient('mongodb://' + db_IP + ':' + str(db_port) + '/')
    db = db_client[db_name]
    silo_entry = db[v_silo_collection].find_one({"vSiloID": v_silo_id})

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
    ########################################################

    # fetch env parameters
    # tenant_id = os.environ["tenantID"]
    # flavourParams = os.environ["flavourParams"]
    # v_silo_id = os.environ["vSiloID"]
    # virIoT_mqtt_data_broker_IP = os.environ["MQTTDataBrokerIP"]
    # virIoT_mqtt_data_broker_port = int(os.environ["MQTTDataBrokerPort"])
    # virIoT_mqtt_control_broker_IP = os.environ["MQTTControlBrokerIP"]
    # virIoT_mqtt_control_broker_port = int(os.environ["MQTTControlBrokerPort"])
    # db_IP = os.environ['systemDatabaseIP']  # IP address of system database
    # db_port = os.environ['systemDatabasePort']  # port of system database
    db_client.close()   # Close DB connection
    print("Starting vSilo controller")

    # function mapping
    init_Broker = init_Mobius
    on_delete_vThing_on_Broker = on_delete_vThing_Mobius
    on_add_vThing_on_Broker = on_add_vThing_Mobius
    on_vThing_data_on_Broker = on_vThing_data_Mobius
    on_commandRequest_on_Broker = on_commandRequest_Mobius

    # Mongodb settings
    # db_name = "viriotDB"  # name of system database
    # v_thing_collection = "vThingC"
    # thing_visor_collection = "thingVisorC"

    # Init Broker
    BROKER_IP = "127.0.0.1"
    BROKER_HTTP_PORT = 7579
    BROKER_MQTT_PORT = 1883
    BROKER_MQTT_TOPIC = "/oneM2M/req/Mobius/"+v_silo_id+"/json"
    init_Broker()

    # MQTT clients setup
    # MQTT client for data messages exchange with VirIoT
    mqtt_virIoT_control_client = mqtt.Client()
    # MQTT client for control messages exchange with VirIoT
    mqtt_virIoT_data_client = mqtt.Client()
    # MQTT client for messages exchange with vSilo Broker
    mqtt_broker_client = mqtt.Client()

    # Start MQTT loops
    mqtt_virIoT_data_client.connect(virIoT_mqtt_data_broker_IP,
                                    virIoT_mqtt_data_broker_port, 10)
    mqtt_virIoT_data_client.message_callback_add(
        v_silo_prefix + "/" + v_silo_id + "/" + data_in_suffix, on_vThing_data)
    mqtt_virIoT_data_client.subscribe(
        v_silo_prefix + "/" + v_silo_id + "/" + data_in_suffix)
    mqtt_virIoT_data_client.loop_start()

    mqtt_virIoT_control_client.connect(
        virIoT_mqtt_control_broker_IP, virIoT_mqtt_control_broker_port, 10)
    mqtt_virIoT_control_client.message_callback_add(
        v_silo_prefix + "/" + v_silo_id + "/" + control_in_suffix, on_in_control_msg)
    mqtt_virIoT_control_client.subscribe(
        v_silo_prefix + "/" + v_silo_id + "/" + control_in_suffix)
    mqtt_virIoT_control_client.loop_start()

    mqtt_broker_client.connect(
        BROKER_IP, BROKER_MQTT_PORT, 10)
    mqtt_broker_client.message_callback_add(
        BROKER_MQTT_TOPIC, on_commandRequest_on_Broker)
    mqtt_broker_client.subscribe(BROKER_MQTT_TOPIC)
    mqtt_broker_client.loop_start()

    # restore virtual things found in the systemDB. It is useful after vSilo crash and restore (e.g. by k8s)
    restore_virtual_things()

    while True:
        try:
            time.sleep(3)
        except:
            print("KeyboardInterrupt"+"\n")
            time.sleep(1)
            os._exit(1)
