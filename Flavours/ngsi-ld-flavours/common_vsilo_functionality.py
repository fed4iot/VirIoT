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

# generic virtual Silo controller code

import os
import sys
import time
import signal
import traceback
import paho.mqtt.client as mqtt
import json
import argparse
from importlib import import_module
from threading import Thread
from pymongo import MongoClient
from bson.json_util import dumps
from concurrent.futures import ThreadPoolExecutor
# requests only needed because we may be a System vSilo
# thus in need to talk REST to master controller
import requests
# google's leveldb is used as a persistent on-disk hashmap
# where we keep track of what entity ids are under the same vthingid.
# It is thread-safe, so we use it to also signal if the vthing is already
# created (and we can proceed with data insert in parallel), or by
# removing it (and we block the parallel ongoing data insert)
# I MAY GET RID OF THIS if the NGSI-LD Broker supports the query "get all entities with this property having this value,
# REGARDLESS the entity type" as was specified in version 1.3.1 of the API
import plyvel
# the following is used to delete the folder of the on-disk hashmap at startup
# and in production would not be needed because we only run dockerized and
# we always are going to startup with a fresh filesystem
import shutil


# -*- coding: utf-8 -*-

# Import flask

from flask import Flask
from flask import json
from flask import request

# Flask: define app

app = Flask(__name__)

# add flask nuri endpoint, so that we can receive notifications from broker
@app.route('/receive_notification_from_broker/<attr>', methods=['POST'])
def recv_notify(attr):
    # unpack notifications and send it to the thingvisor
    # first thing to do is print the received notification to observe its structure
    # and find the cmd_request object inside the notification
    # as a "value" of a property named as one of the possible commands of this entity
    print("Received notification from broker on \""+attr+"\" attr")
    try:
        r = request.get_json()
        if type(r) is dict:
            jres = r
        else:
            jres = json.loads(r)
    except Exception as err:
        print("Bad notification format", err)
        return 'Bad notification format', 401
    
    entity=jres['data'][0]
    if attr in entity:
        if 'cmd-id' in entity[attr]['value']:
            # in any case lets overwrite the nuri, to avoid injecting a malicious nuri
            # so, not only if 'cmd-nuri' not in entity[attr]['value']:
            entity[attr]['value']['cmd-nuri'] = 'viriot://vSilo/'+v_silo_id+'/data_in'
            # BEWARE HERE that 'object' is ok if generatedByVThing is a Relationship
            # but if it is a Property, then it has to be 'value'. This may be the case
            # because some NGSI-LD Brokers (maybe Stellio) do not allow dangling Relationships.
            # This is why we decided to use Property instead of Relationship.
            vThingID=entity['generatedByVThing']['value']

            cmd_value = entity[attr]['value']
            cmd_name = attr
            cmd_LD_ID = entity['id']
            cmd_LD_Type = entity['type']
            print("Sending command out...")
            send_command_out(cmd_LD_ID, cmd_LD_Type,cmd_name, cmd_value, vThingID)

    #print(jres)
    # return ""
    return 'OK'

# Thread for running Flask
class FlaskThread(Thread):
    def __init__(self):
        Thread.__init__(self)
        
    def run(self):
        print("Starting Flask...")
        app.run(host="0.0.0.0", port="5555")


def send_command_out(cmd_LD_ID, cmd_LD_Type, cmd_name, cmd_value, vThingID):
    ngsiLdEntity = {"id": cmd_LD_ID, "type": cmd_LD_Type,
                    cmd_name: {"type": "Property", "value": cmd_value}}
    data = [ngsiLdEntity]
    topic = "vThing/"+vThingID+"/data_in"
    # publish changed status
    message = {
        "data": data, 
        "meta": {
            "vSiloID": v_silo_id,
            "vThingID": vThingID
        }
    }  # neutral-format
    future = executor.submit(publish_on_virIoT, message, topic)
    #publish_on_virIoT(message, topic)
    return

def publish_on_virIoT(message, out_topic):
    msg = json.dumps(message)
    print("Message sent on "+out_topic + "\n" + msg+"\n")
    # publish data to out_topic
    mqtt_data_client.publish(out_topic, msg)

# The callbacks for when the client receives a CONNACK response from the server.
def mqtt_data_on_connect(client, userdata, flags, rc):
    print("MQTT data channel connected with result code "+str(rc))
    client.message_callback_add(in_vsilo_data_topic, mqtt_on_in_vsilo_datatopic_message)
    client.subscribe(in_vsilo_data_topic)
    global connected_clients
    connected_clients += 1


def mqtt_data_on_disconnect(client, userdata, rc):
    if rc != 0:
        print("Unexpected MQTT data channel disconnection.")
    else:
        print("MQTT data channel disconnection.")
    #global connected_clients
    #connected_clients -= 1
    client.reconnect()

# We immediately (on startup) subscribe to:
# - [see above] the data messages unicast sent to this specific vSilo via its in_vsilo_data_topic
# (data_in) topic. This is the unicast topic used in the actuation workflow.
# - the control messages coming into this vSilo (i.e. published by others on the in_vsilo_control_topic
# of this vSilo).
# - If we are a System vSilo we also subscribe to (createVThing) control messages being spit out to the
# thing_visor_prefix + '/' + tv_id + '/' + out_control_suffix
# (for instance: TV/tv123/c_out) by EACH TV, BUT we don't know all TVs identifiers.
# Can we subscribe to TV/# ? No, because we would also
# get all DATA being spit out by TVs.... so we use generic single-level wildcard: TV/+/c_out
def mqtt_control_on_connect(client, userdata, flags, rc):
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    # Add message callback and subscription for receiving control messages of this silo
    client.message_callback_add(in_vsilo_control_topic, mqtt_on_in_vsilo_controltopic_message)
    client.subscribe(in_vsilo_control_topic)
    # Add message callback and subscription for receiving control messages from all TVs
    # But only if we are a System vSilo
    if is_this_vsilo_systemvsilo == True:
        client.message_callback_add(out_generic_thingvisor_control_topic, mqtt_on_out_generic_thingvisor_controltopic_message)
        client.subscribe(out_generic_thingvisor_control_topic)

    print("MQTT control channel connected with result code "+str(rc))
    global connected_clients
    connected_clients += 1


def mqtt_control_on_disconnect(client, userdata, rc):
    if rc != 0:
        print("Unexpected MQTT control channel disconnection.")
    else:
        print("MQTT control channel disconnection.")
    #global connected_clients
    #connected_clients -= 1
    client.reconnect()


# Utility function
def message_to_jres(message):
    payload = message.payload.decode("utf-8", "ignore")
    jres = json.loads(payload.replace("\'", "\""))
    return jres


# This is the set of callbacks that receive ALL messages (both
# from the control_client and from the data_client).
#
# The control_client is subscribed to:
# -- messages of the in_vsilo_control_topic of this vSilo (remind that client has subscribed at silo startup)
# -- messages of the out_vthing_control topic (suffix control_out) of the vThings this silo has dynamically added to itself
# -- in case of System vSilo, control messages being spit out to the thing_visor_prefix /tv_id/out_control_suffix
# (for instance: TV/tv123/c_out) by each TV, so that we can capture
# createVThing messages and produce a corresponding addVThing in order to inject all data/entities
# into the System vSilo. BUT we don't know all TVs identifiers. Can we subscribe to TV/# ?
# No, because we would also get all DATA being spit out by TVs.... so we use single-level wildcard: TV/+/c_out
# The data_client is subscribed to:
# -- messages of the out_vthing_datatopic (data_out suffix) of the vThings this silo has dynamically added to itself
#
# We spawn a thread upon receiving a new message, to handle the time-consuming
# processing of the message and direct it to the appropriate function. Basically we
# start a background worker thread to take care of the message
# and of the time consuming operations involving interaction with external
# broker and network resources and we can immediately return so as to free
# the callback for receiving other MQTT messages.
#
# TODO Please also consider the general problem that msgs are received asynchronously, so
# that while i am processing, say, a delete vThing, i can receive an add vThing in parallel
# and this will result into problems
#
# Specific callbacks for the above follow:

# this vsilo control
def mqtt_on_in_vsilo_controltopic_message(client, userdata, message):
    executor.submit(process_in_vsilo_control_msg, message)

def mqtt_on_in_vsilo_datatopic_message(client, userdata, message):
    # executor.submit(data_insert_entities_under_vThing, message)
    executor.submit(batch_data_insert_entities_under_vThing, message)

# our vthings control
def mqtt_on_out_vthing_controltopic_message(client, userdata, message):
    executor.submit(process_out_vthing_control_msg, message)

# our vthings data
def mqtt_on_out_vthing_datatopic_message(client, userdata, message):
    # messages to vthing's data_out topic contain entities to be inserted in our broker
    # executor.submit(data_insert_entities_under_vThing, message)
    executor.submit(batch_data_insert_entities_under_vThing, message)

# any thingvisor control
def mqtt_on_out_generic_thingvisor_controltopic_message(client, userdata, message):
    executor.submit(process_out_generic_thingvisor_control_msg, message)


# BEGIN SYSTEM VSILO =====================================================================
# System vSilo processing commands coming from thing visors ==============================
def process_out_generic_thingvisor_control_msg(message):
    jres = message_to_jres(message)
    print("Process out_generic_thingvisor_control has " + str(connected_clients) + " connected clients")
    commandType = jres['command']
    if commandType == "createVThing":
        print("TV COMMAND create vThing " + json.dumps(jres))
        # see Master-controller.py function on_message_create_vThing(jres)
        # to extract these metafields
        v_thing = jres["vThing"]
        v_thing_id = v_thing["id"]
        tv_id = jres["thingVisorID"]
        # Now /login as admin and get back the admin token
        token = login_as_admin_and_get_token()
        if token != "":
            # Now /addVThing to this vSilo
            invoke_REST_add_vthing(token, v_thing_id)
            print("OK create command from TV " + tv_id + " was mirrored to an add System vSilo vThing " + v_thing_id)
    else:
        print("invalid from TV incoming command " + commandType)


# the following method is basically a copy of f4i_login.py
def login_as_admin_and_get_token():
    url = controllerurl+"/login"

    # tenant_id is == "admin"
    payload = {"userID": tenant_id, "password": adminpassword}
    print("  System vSilo logging as admin to mastercontroller url: " + controllerurl)
    #print("\n"+json.dumps(payload)+"\n")

    headers = {
        'accept': "application/json",
        'content-type': "application/json",
        'cache-control': "no-cache",
    }

    response = requests.request("POST", url, data=json.dumps(payload), headers=headers)

    if response.status_code in [201, 200]:
        token = response.json()["access_token"]
        return token
    else:
        print("    System vSilo could NOT login as admin to mastercontroller url: " + controllerurl)
        print("    " + response.text + "\n")
        # this empty return is crucial to signal a bad thing has occurred
        return ""


# the following method is basically a copy of f4i_add_vthing.py
# We have to pass to it the token and the v_thing_id, while v_silo_id is global
def invoke_REST_add_vthing(token, v_thing_id):
    url = controllerurl + "/addVThing"
    # split at the first "_" starting from left, and take the first string of the resulting list
    # "admin_SystemSilo1" gives back "admin"
    v_silo_name = v_silo_id.split("_", 1)[1]
    print("  System vSilo " + v_silo_name + " adding vThing " + v_thing_id + " to itself via mastercontroller url: " + controllerurl)

    payload = "{\n\t\"tenantID\":\"" + tenant_id + "\",\n" \
                                                   "\t\"vThingID\":\"" + v_thing_id + "\",\n" \
                                                                                      "\t\"vSiloName\":\"" + v_silo_name + "\"}"

    headers = {
        'Authorization': "Bearer " + token,
        'accept': "application/json",
        'content-type': "application/json",
        'cache-control': "no-cache",
    }

    response = requests.request("POST", url, data=payload, headers=headers)
    print("    System vSilo /addVThing POST response: " + response.text + "\n")

# END SYSTEM VSILO ==================================================================================================


# vsilo incoming control messages switch and process
def process_in_vsilo_control_msg(message):
    jres = message_to_jres(message)
    print("Process in_vsilo_control has " + str(connected_clients) + " connected clients")
    commandType = jres['command']
    if commandType == "addVThing":
        print("COMMAND add vThing " + json.dumps(jres))
        v_thing_id = jres['vThingID']
        control_add_vThing(v_thing_id)
        return "adding vThing"
    elif commandType == "deleteVThing":
        print("COMMAND delete vThing " + json.dumps(jres))
        v_thing_id = jres['vThingID']
        control_delete_vThing(v_thing_id)
        return "deleting vThing"
    elif commandType == "destroyVSilo":
        print("COMMAND destroy vSilo " + json.dumps(jres))
        control_destroy_vSilo()
        return "destroying vSilo"
    elif commandType == "getContextResponse":
        print("COMMAND received getContextResponse " + json.dumps(jres))
        print("COMMAND received STARTING RECONSTRUCTING A CONTEXT FOR A VTHING")
        #del jres["command"] # this is unnecessary because the command field is not inspected in data_insert_entities_under_vThing
        # so i can safely forward the message itself insted of the jres, which is good because
        # conversion into a jres happens later and is part of the future executor
        #data_insert_entities_under_vThing(message)
        batch_data_insert_entities_under_vThing(message)
        print("COMMAND received JUST FINISHED RECONSTRUCTING A CONTEXT FOR A VTHING")
        return "received context response"
    else:
        print("invalid incoming command " + commandType)


# execute add vThing operations:
# The idea here is to just activate the vthing in the silo controller, by flagging
# it as active in the hashmap, and then just leave to the insert_data method the job of adding
# elements under the vthingid in the hashmap, as they arrive (please notice that data starts to
# arrive already here, because we here fetch the context for the vthing we are adding).
def control_add_vThing(v_thing_id):
    print("STARTING TO ADD A VTHING...")
    try:
        # first of all, flag inside our hashmap that we want to (re)activate a vthing
        activate_vThing_in_hashmap(v_thing_id)
        # after that, first create data structures fo the vthing on the Broker (if any...)
        print("... trying to add vthing " + v_thing_id + " to broker")
        result = brokerspecific.create_vThing_on_Broker(v_thing_id)
        # then subscribe, to start receiving data
        if result:
            # add subscription for virtual Thing out data topic (on mqtt data client)
            out_vthing_datatopic = v_thing_prefix + '/' + v_thing_id + '/' + out_data_suffix
            mqtt_data_client.subscribe(out_vthing_datatopic)
            mqtt_data_client.message_callback_add(out_vthing_datatopic, mqtt_on_out_vthing_datatopic_message)
            print("... subscribed to vThing data topic: " + out_vthing_datatopic)
            # add subscription for virtual Thing out control topic (on mqtt control client)
            out_vthing_controltopic = v_thing_prefix + '/' + v_thing_id + '/' + out_control_suffix
            mqtt_control_client.subscribe(out_vthing_controltopic)
            mqtt_control_client.message_callback_add(out_vthing_controltopic, mqtt_on_out_vthing_controltopic_message)
            print("... subscribed to vThing out control topic: " + out_vthing_controltopic)
            # retrieve last context for the virtual thing from the thing visor
            fetch_last_context_for_vthing(v_thing_id)
            print("... adding vthing " + v_thing_id + " SUCCESS")
            return 'OK'
        else:
            print("... adding vthing " + v_thing_id + " FAIL!!")
            return 'Creation vThing fails'
    except Exception as ex:
        traceback.print_exc()
        return 'ERROR'


# When deleting a vThing the idea is to first stop the incoming data stream
# for the vThing by unsubscribing, and then remove all objects from
# the broker that are under the vThing, so that we do not receive data meanwhile removing
# Please also consider the general problem that msgs are received asynchronously, so
# that while i am processing this delete, i can receive an add vThing in parallel
# and this will result into problems, if we don't use a thread-safe data structure
# such as the leveldb on-disk hashmap
def control_delete_vThing(v_thing_id):
    print("STARTING TO DELETE A VTHING...")
    try:
        # Lets do a safety check that the vthing is active in the hashmap
        if check_if_vThing_is_in_hashmap(v_thing_id) == False:
            print("STRANGE WARNING that you want to delete vThing " + v_thing_id + " that i dont have in hashmap")
        deactivate_vThing_in_hashmap(v_thing_id)
        # removing mqtt subscriptions and callbacks
        out_vthing_datatopic = v_thing_prefix + '/' + v_thing_id + '/' + out_data_suffix
        mqtt_data_client.message_callback_remove(out_vthing_datatopic)
        mqtt_data_client.unsubscribe(out_vthing_datatopic)
        print("... UNsubscribed to vThing data topic: " + out_vthing_datatopic)
        out_vthing_controltopic = v_thing_prefix + '/' + v_thing_id + '/' + out_control_suffix
        mqtt_control_client.message_callback_remove(out_vthing_controltopic)
        mqtt_control_client.unsubscribe(out_vthing_controltopic)
        print("... UNsubscribed to vThing out control topic: " + out_vthing_controltopic)
        # TODO At this point subscriptions are removed: it could be the case that we
        # TODO fail the subsequent remove_entities_from_vThing but subscriptions are
        # TODO removed all the same. Is this ok?
        # Now remove entities from the vThing
        # result1 = remove_entities_under_vThing(v_thing_id)
        result1 = batch_remove_entities_under_vThing(v_thing_id)
        print("... trying to delete vthing " + v_thing_id + " from broker")
        result2 = brokerspecific.remove_vThing_from_Broker(v_thing_id)
        if result1 and result2:
            print("... deleting vthing " + v_thing_id + " SUCCESS")
            return 'OK'
        else:
            print("... delete vthing " + v_thing_id + " FAIL!!")
            return 'Delete vThing fails'
    except Exception:
        traceback.print_exc()
        return 'ERROR'


def control_destroy_vSilo():
    send_destroy_v_silo_ack_message()
    mqtt_control_client.disconnect()
    print("Shutdown completed")


def send_destroy_v_silo_ack_message():
    msg = {"command": "destroyVSiloAck", "vSiloID": v_silo_id}
    mqtt_control_client.publish(out_vsilo_control_topic, str(msg).replace("\'", "\""))


# vthing outgoing control messages switch and process
# to capture control commands sent out by the vThing
def process_out_vthing_control_msg(message):
    jres = message_to_jres(message)
    print("Process out_vthing_control has " + str(connected_clients) + " connected clients. jres is " + json.dumps(jres))
    # we are the silo controller: when we receive a deleteVThing message that
    # has been published (by a vThing) on the vthingID/out_control channel, we react here
    if jres["command"] == "deleteVThing":
        #msg = {"vThingID": jres["vThingID"]}
        v_thing_id = jres["vThingID"]
        control_delete_vThing(v_thing_id)
    else:
        # TODO manage other commands
        print('vthing outgoing command not managed ' + jres["command"])


def fetch_last_context_for_vthing(v_thing_id):
    message = {"command": "getContextRequest", "vSiloID": v_silo_id, "vThingID": v_thing_id}
    mqtt_control_client.publish(v_thing_prefix + "/" + v_thing_id + "/" + in_control_suffix, str(message).replace("\'", "\""))
    print("... command to fetch last context for vthing " + v_thing_id + " SENT")


def restore_virtual_things():
    # Retrieve from system db the list of virtual things in use and restore them.
    # This is needed in case of silo controller crashing and then restarting.
    # In case i am a System vSilo, i should scan all vThings of all ThungVisors, regardless
    # wether the vThings have actually been added to any vSilo. So we have to
    # fetch them from the ThingVisors directly (because if the System vSilo starts
    # AFTER the ThingVisor, it would not capture the create_vthing message from the TV
    db_client = MongoClient('mongodb://' + db_IP + ':' + str(db_port) + '/')
    db = db_client[db_name]

    if is_this_vsilo_systemvsilo == False:
        connected_v_things = json.loads(dumps(db[v_thing_collection].find({"vSiloID": v_silo_id}, {"vThingID": 1, "_id": 0})))
    else:
        connected_v_things = []
        v_things_entries = db[thing_visor_collection].find({}, {"_id": 0, "vThings": 1})
        for vThingEntry in v_things_entries:
            for vThing in vThingEntry["vThings"]:
                # now in vThing i have a description of a vThing as seen from the ThingVisor, that
                # is made of "id", "label" and "description". I only extract "id" and rename it "vThingID"
                # and create a simple object that i append to the resulting array
                simple_vthing = {'vThingID':vThing['id']}
                connected_v_things.append(simple_vthing)

    if len(connected_v_things) > 0:
        for vThing in connected_v_things:
            if "vThingID" in vThing:
                print("restoring virtual thing with ID: " + vThing['vThingID'])
                control_add_vThing(vThing['vThingID'])


# ========== HASHMAP
def check_if_vThing_is_in_hashmap(v_thing_id):
    key = v_thing_id.encode()
    if leveldb.get(key) == None:
        return False
    else:
        return True


def activate_vThing_in_hashmap(v_thing_id):
    print("-> activating vthing " + v_thing_id + " in hashmap")
    # by inserting the vthingID as key, and a dummy value as value
    key = v_thing_id.encode()
    value = b'dummy'
    leveldb.put(key, value)


def deactivate_vThing_in_hashmap(v_thing_id):
    print("-> deactivating vthing " + v_thing_id + " in hashmap")
    key = v_thing_id.encode()
    leveldb.delete(key)


# ========== HASHMAP + BROKER

# Here we receive a data item, which is composed of "data" and "meta" fields
def data_insert_entities_under_vThing(message):
    jres = message_to_jres(message)
    v_thing_id = jres['meta']['vThingID']
    print("STARTING TO INSERT ENTITIES UNDER VTHING " + v_thing_id)
    # (in this method we should track what NGSI-LD entities are under the same vThing)
    # We receive jres as a dictionary.
    if leveldb.get(v_thing_id.encode()) != None:
        data = jres['data']
        # data is the array of NGSI-LD entities, that has now become a python list which we loop
        for entity in data:
            # first of all try to add the NGSI-LD entity in the broker
            if brokerspecific.add_or_modify_entity_under_vThing_on_Broker(v_thing_id, entity):
                # then track what NGSI-LD entities are under the same vThing:
                # We now better do it with the hashmap, by creating a key composed of
                # a prefix and a suffix. Prefix is the vthingid, suffix is the entity id
                # so that keys are different, but have a common prefix to fetch them as a group.
                # We then redund the entity id also as a value to speed things up when we get it back
                # and he @@ separator is just to visually separate, not to call a string.split()
                # The prefixed vthingid is used to group and fast-get just the elements of
                # one specific vthingid, because the leveldb hashmap is ordered lexicographycally, and
                # we can jump to a set of keys which begin_with() something.
                key = (v_thing_id + "@@" + entity['id']).encode()
                value = entity['id'].encode()
                leveldb.put(key, value)
            else:
                print("Exception while REST ADD of Entity " + entity['id'] + " under vThing " + v_thing_id)
    else:
        print(" DATA HAS ARRIVED FOR NON ACTIVE vThing " + v_thing_id + ". Skipping it.")

    # return ok in any case
    return 'OK'


    # Here we receive a data item, which is composed of "data" and "meta" fields
def batch_data_insert_entities_under_vThing(message):
    jres = message_to_jres(message)
    v_thing_id = jres['meta']['vThingID']
    print("STARTING TO INSERT ENTITIES UNDER VTHING " + v_thing_id)
    data = jres['data']
    # data is the array of NGSI-LD entities, that has now become a python list which we loop
    try:
        batch_op_success = brokerspecific.batch_add_or_modify_entity_under_vThing_on_Broker(v_thing_id, data)
    except Exception as ex:
        traceback.print_exc()

    print('BATCH_ENTITY IDs SUCCESSFULLY CREATED: ', batch_op_success)
    # after_batch_data is the result list you receive when you do a batch operation containing the id of all the entities created/updated
    for entity in data:
        # checking if the id of the entity is in the list of successes, than adding it to the hashmap
        if entity['id'] not in batch_op_success:
            print("Exception while REST ADD of Entity " + entity['id'] + " under vThing " + v_thing_id)
        else:
            key = (v_thing_id + "@@" + entity['id']).encode()
            value = entity['id'].encode()
            leveldb.put(key, value)

    # return ok in any case
    return 'OK'



# Here we receive a vthing id
def remove_entities_under_vThing(v_thing_id):
    print("STARTING TO REMOVE ENTITIES UNDER VTHING " + v_thing_id)
    # Here we should remove all NGSI-LD entities that are under the same vThing.
    # At this point the sentinel entry, which signals in the hashmap that we have the vthing as active,
    # has already been deactivetad/removed. But we still have all the mappings, so that we can use
    # them to physically remove entities from the Broker.
    # We get the entities to delete by asking the hashmap for all values
    # that are prefixed by the same vthingID
    entities_ids = []
    prfx = v_thing_id.encode()
    # then we prepare to batch remove the set of keys from the hashmap
    try:
        with leveldb.write_batch() as b:
            for key, value in leveldb.iterator(prefix=prfx):
                entities_ids.append(value.decode())  
                # lets now delete the entity from the Broker
                if brokerspecific.delete_entity_under_vThing_on_Broker(v_thing_id, value.decode()):
                    b.delete(key)
                else:
                    print("Exception while REST DELETE of Entity " + value.decode())
            # here we exit the "with" context and the batch.write() is automatically executed
        print("    finished physically removing on Broker vthing " + v_thing_id)
        print("IDs deleted:", entities_ids)
    except Exception as ex:
        traceback.print_exc()
    return True




def batch_remove_entities_under_vThing(v_thing_id):
    print("STARTING TO REMOVE ENTITIES UNDER VTHING " + v_thing_id)
    # Here we should remove all NGSI-LD entities that are under the same vThing.
    # We achieve this by querying all the entities using the v_thing_id
    # and then deleting all of them using the ids we gather
    # NOTE: This is not working for all the NGSI-LD Flavours (only Orion-LD supports it)
    #       so for now we use a workaround with the Hash-Map
    #entities = brokerspecific.get_all_entities_under_vThing_on_Broker(v_thing_id)
    #entities_ids = [entity['id'] for entity in entities]
    #batch_delete_success = brokerspecific.batch_entity_delete_under_vThing_on_Broker(v_thing_id,entities_ids)

    entities_ids = []
    prfx = v_thing_id.encode()
    # We get all the IDs to delete under a vThing from the Hash Map
    try:
        with leveldb.write_batch() as b:
            for key, value in leveldb.iterator(prefix=prfx):
                entities_ids.append(value.decode())  
                # lets now delete the entity from the Broker
                b.delete(key)
        print("IDs candidated to delete:", entities_ids)
        batch_delete_success = brokerspecific.batch_entity_delete_under_vThing_on_Broker(v_thing_id,entities_ids)
        print("IDs actually deleted:", batch_delete_success)
    except Exception as ex:
        traceback.print_exc()


    print("DELETE finished physically removing on Broker vthing " + v_thing_id)
    return True

def check_if_vThing_is_in_Broker(v_thing_id):
    # We get all the entities giving a v_thing_id
    # if the len of the data array we get is greater than 0
    # Then the vThing is active
    entities = brokerspecific.get_all_entities_under_vThing_on_Broker(v_thing_id)
    if len(entities) > 0:
        return True
    else:
        return False



# ========== END HASHMAP + BROKER


def handler(signal, frame):
    global mqtt_data_client
    global mqtt_control_client
    print("HANDLING")
    mqtt_data_client.loop_stop()
    mqtt_control_client.loop_stop()
    clean_close()


def clean_close():
    global connected_clients
    connected_clients = 0
    mqtt_data_client.disconnect()
    mqtt_control_client.disconnect()
    leveldb.close()
    sys.exit()


def start_silo_controller(broker_specific_module_name):
    signal.signal(signal.SIGINT, handler)
    
    global v_silo_prefix
    global v_thing_prefix
    global in_control_suffix
    global out_control_suffix
    global in_data_suffix
    global out_data_suffix
    global in_vsilo_control_topic
    global out_vsilo_control_topic
    global out_generic_thingvisor_control_topic
    global in_vsilo_data_topic
    global mqtt_control_client
    global mqtt_data_client
    global connected_clients
    global leveldb
    global db_IP
    global db_port
    global db_name
    global v_thing_collection
    global thing_visor_collection
    global v_silo_id
    global brokerspecific
    global tenant_id
    global is_this_vsilo_systemvsilo
    global controllerurl
    global adminpassword
    global executor

    # lets import the silo-controller-specific functions and bind them into us
    print("importing module: " + broker_specific_module_name)
    brokerspecific = import_module(broker_specific_module_name)

    # threadPoolExecutor default size is number of CPUs
    executor = ThreadPoolExecutor()

    # connect to the on-disk hashmap
    shutil.rmtree('plyvelhashmap', ignore_errors=True)
    leveldb = plyvel.DB('plyvelhashmap', create_if_missing=True)

    # If you run this silo controller MANUALLY for DEBUG PURPOSES,
    # then you may access the -d parameter to set a local address of the mongo DB
    # and a local MQTT. This parameter is never visible when this silo
    # is run via docker automatism (or similar) via the master controller.
    parser = argparse.ArgumentParser(description='A vSilo Controller.')
    parser.add_argument('-d', '--debug_mongo_ip', dest='debug_mongo_ip', help='run in debug mode and use the given IP address of the system MongoDB (usually 172.17.0.2)')
    parser.add_argument('-p', '--debug_flavour_params', dest='debug_flavour_params', help='use the given flavour params (a {JSON object}) for debug purposes')
    args = parser.parse_args()

    # flavour_params must be a string
    if args.debug_mongo_ip != None and args.debug_flavour_params != None:
        # -------------- DEBUG PARAMETERS --------------
        tenant_id = "tenant1"
        v_silo_id = "tenant1_Silo1"
        virIoT_mqtt_data_broker_IP = "127.0.0.1"
        virIoT_mqtt_data_broker_port = 1883
        virIoT_mqtt_control_broker_IP = "127.0.0.1"
        virIoT_mqtt_control_broker_port = 1883
        flavour_params = args.debug_flavour_params
        db_IP = args.debug_mongo_ip
        db_port = 27017
        print("starting silo controller in DEBUG mode to " + db_IP)
    else:
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

        valid_silo_entry = False
        for x in range(MAX_RETRY):
            if silo_entry is not None:
                valid_silo_entry = True
                break
            time.sleep(3)

        if not valid_silo_entry:
            print("Error: Virtual Silo entry not found for v_silo_id:", v_silo_id)
            sys.exit(1)

        try:
            # import information from DB
            tenant_id = silo_entry["tenantID"]
            virIoT_mqtt_data_broker_IP = silo_entry["MQTTDataBroker"]["ip"]
            virIoT_mqtt_data_broker_port = int(silo_entry["MQTTDataBroker"]["port"])
            virIoT_mqtt_control_broker_IP = silo_entry["MQTTControlBroker"]["ip"]
            virIoT_mqtt_control_broker_port = int(silo_entry["MQTTControlBroker"]["port"])
            
            # in this flavour, params is the silo type (System vSilo or not, and the brokerport)
            # Fetch them from DB, unless they were given for debug purpose on command line
            if args.debug_flavour_params != None:
                flavour_params = args.debug_flavour_params
                print("Fetching params JSON object from command line")
            else:
                print("Fetching params JSON object from DB")
                flavour_params = silo_entry["flavourParams"]
                if not flavour_params:
                    flavour_params = '{}'
        except Exception as e:
            print("Error: Vital information not found in silo_entry", e)
            sys.exit(1)

        db_client.close()   # Close DB connection
        print("starting silo controller")

    # start the flask thread
    print("Starting Flask thread...")
    flask_thread = FlaskThread()
    flask_thread.start()

    print("This silo's tenant ID is: " + tenant_id)
    # in this flavour, param is the silo type (Raw, Mobius, FiWare, ..., or SystemvSilo)
    # and in case this is a System vSilo, the admin password and the master controller
    # urlshall be issued, too,
    # because this silo needs to talk to the master controller and
    # programmatically add each and every vThing that enters the platform
    # via a POST to /addVThing REST interfce of master controller
    print(v_silo_id + " got flavour params: " + flavour_params)
    try:
        params = json.loads(flavour_params.replace("'", '"'))
    except (json.decoder.JSONDecodeError, KeyError):
        print("  ...that cannot be decoded to JSON. Exiting!!!")
        sys.exit(1)
    if "flavourtype" in params:
        flavourtype = params['flavourtype']
    else:
        flavourtype = ""
    if "adminpassword" in params:
        adminpassword = params['adminpassword']
    else:
        adminpassword = ""
    if "controllerurl" in params:
        controllerurl = params['controllerurl']
    else:
        controllerurl = ""
    if "brokerport" in params:
        brokerport = params['brokerport']
    else:
        brokerport = 1026
    if flavourtype == "systemvsilo" and tenant_id == "admin" and controllerurl != "":
        is_this_vsilo_systemvsilo = True
    else:
        is_this_vsilo_systemvsilo = False

    print("Is this silo a System vSilo?: " + str(is_this_vsilo_systemvsilo))

    # Mongodb settings
    db_name = "viriotDB"  # name of system database
    v_thing_collection = "vThingC"
    thing_visor_collection = "thingVisorC"

    # initialize whatever broker we have, before receiving messages!
    brokerspecific.init_Broker(brokerport)

    # MQTT settings
    v_silo_prefix = "vSilo"  # prefix name for virtual IoT System communication topic
    v_thing_prefix = "vThing"  # prefix name for virtual Thing data and control topics
    thing_visor_prefix = "TV"  # prefix name for ThingVisor communication topic
    in_control_suffix = "c_in"
    out_control_suffix = "c_out"
    in_data_suffix = "data_in"
    out_data_suffix = "data_out"
    # useful strings setup:
    # the following topic is used by us to subscribe to control commands directed to us
    in_vsilo_control_topic = v_silo_prefix + "/" + v_silo_id + "/" + in_control_suffix
    # the following topic is just used by us to publish ACK messages coming from us
    out_vsilo_control_topic = v_silo_prefix + "/" + v_silo_id + "/" + out_control_suffix
    # generic TV, single-level wildcard: TV/+/c_out
    out_generic_thingvisor_control_topic = thing_visor_prefix + "/+/" + out_control_suffix
    # the following topic is used by us to subscribe to data in of this TV and get the data after actuation commands
    in_vsilo_data_topic = v_silo_prefix + "/" + v_silo_id + "/" + in_data_suffix
    # create and start two clients for MQTT
    mqtt_control_client = mqtt.Client()
    mqtt_data_client = mqtt.Client()
    connected_clients = 0
    mqtt_data_client.on_disconnect = mqtt_data_on_disconnect
    mqtt_data_client.on_connect = mqtt_data_on_connect
    mqtt_control_client.on_disconnect = mqtt_control_on_disconnect
    mqtt_control_client.on_connect = mqtt_control_on_connect
    mqtt_data_client.connect(virIoT_mqtt_data_broker_IP, virIoT_mqtt_data_broker_port)
    mqtt_control_client.connect(virIoT_mqtt_control_broker_IP, virIoT_mqtt_control_broker_port)

    # enter the connect loop
    print("Entering connect loop")
    while connected_clients < 2:
        mqtt_data_client.loop()
        mqtt_control_client.loop()

    print("Restoring virtual things")
    restore_virtual_things()
    print("Restored and init finished")

    # starting the two threads, each for each mqtt client we have
    print("Entering main network loop")
    mqtt_data_client.loop_start()
    mqtt_control_client.loop_start()

    # doing nothing in the main thread
    while True:
        time.sleep(10)

