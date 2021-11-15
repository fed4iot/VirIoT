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

# This is a Fed4IoT ThingVisor generic modular code to import in your custom ThingVisors

import time
import os
import json
import traceback
import requests
import paho.mqtt.client as mqtt
from pymongo import MongoClient
from context import Context
from concurrent.futures import ThreadPoolExecutor
from importlib import import_module

def initialize_vthing(vthingindex, type, description, commands, jsonld_at_context_field = None, id_LD = None):
    if id_LD is None:
        id_LD="urn:ngsi-ld:" + thing_visor_ID + ":" + vthingindex
    
    v_things[vthingindex]={}

    v_things[vthingindex]['name']=vthingindex #detector
    v_things[vthingindex]['type_attr']=type #FaceRecognitionEvent
    v_things[vthingindex]['ID']=thing_visor_ID + "/" + vthingindex #facerec-tv/detector 
    v_things[vthingindex]['label']=vthingindex #detector
    v_things[vthingindex]['description']=description
    v_things[vthingindex]['v_thing']={ #meta information
        "label": v_things[vthingindex]['label'],
        "id": v_things[vthingindex]['ID'],
        "description": v_things[vthingindex]['description']
    }
    v_things[vthingindex]['caching']=False
    # the identifier in the neutral format NGSI-LD of the master entity created by this vthing
    v_things[vthingindex]['ID_LD']=id_LD #urn:ngsi-ld:facerec-tv:detector

    # Context is a "map" of current virtual thing state
    # create and save the Context for the new vThing
    v_things[vthingindex]['context']=Context()

    # set topic to the name of mqtt topic of the specific vThing.
    # When suffixed with "out_data" this becomes the topic on which to publish vThing data
    # When suffixed with "in_data" this becomes the topic to listen to for receiving actuation commands
    # directed to this specific vThing (see: callback_for_mqtt_data_in_vthing)
    # v_thing_prefix is constant "vThing"
    v_things[vthingindex]['topic']=v_thing_prefix + "/" + v_things[vthingindex]['ID'] #vThing/facerec-tv/detector

    v_things[vthingindex]['jsonld_at_context_field']=jsonld_at_context_field

    create_vthing_initial_context(vthingindex,commands)

    # data
    subscribe_vthing_data_in_topic(vthingindex)
    # control
    publish_create_vthing_command(vthingindex)
    subscribe_vthing_control_in_topic(vthingindex)


def subscribe_TV_control_in_topic(client, userdata, flags, rc):
    print("connecting mqtt control")
    # Add message callbacks that will only trigger on a specific subscription match
    client.message_callback_add(tv_control_prefix + "/" + thing_visor_ID + "/" + in_control_suffix, callback_for_mqtt_control_in_TV)
    client.subscribe(tv_control_prefix + "/" + thing_visor_ID + "/" + in_control_suffix)
    print("MQTT control client connected with result code "+str(rc))


def mqtt_control_reconnect(client, userdata, rc):
    if rc != 0:
        print("Unexpected MQTT control channel disconnection.")
    else:
        print("MQTT control channel disconnection.")
    client.reconnect()
    
    
def create_vthing_initial_context(vthingindex, commands):
    print("Creating initial vthing context (commands, initial data...)")
    # at startup we want to renew the "commands" property, in case existing
    # Brokers have an outdated list of "commands". We use the publish_attributes function:
    # each item is an attribute to be injected in the Entity, as follows:
    # {attributename:STRING, attributevalue:WHATEVER, isrelationship:BOOL (optional)}
    publish_attributes_of_a_vthing(vthingindex,
                                    [{
                                    "attributename" : "commands",
                                    "attributevalue" : commands
                                    }] )
    

def subscribe_vthing_data_in_topic(vthingindex):
    # Subscribe mqtt_data_client to the vThing topic
    mqtt_data_client.message_callback_add(v_things[vthingindex]['topic'] + "/" + in_data_suffix, callback_for_mqtt_data_in_vthing)
    mqtt_data_client.subscribe(v_things[vthingindex]['topic'] + "/" + in_data_suffix)
    
    
def publish_create_vthing_command(vthingindex):
    # Publish on the thingVisor out_control topic the createVThing command and other parameters
    message = { "command": "createVThing", "thingVisorID": thing_visor_ID, "vThing": v_things[vthingindex]['v_thing'] }
    mqtt_control_client.publish(tv_control_prefix + "/" + thing_visor_ID + "/" + out_control_suffix, json.dumps(message))


def subscribe_vthing_control_in_topic(vthingindex):
    mqtt_control_client.message_callback_add(v_things[vthingindex]['topic'] + "/" + in_control_suffix, callback_for_mqtt_control_in_vthing)
    mqtt_control_client.subscribe(v_things[vthingindex]['topic'] + '/' + in_control_suffix)


def remove_vthing(vthingindex):
    publish_deleteVThing_command(vthingindex)
    del v_things[vthingindex]


def find_entity_within_context(vthingindex,id_LD):
    context=v_things[vthingindex]['context'].get_all()
    for context_entity in context:
        if context_entity["id"]==id_LD:
            return context_entity
    return None


def get_silo_name(nuri):
    return nuri.split('/')[-2]


def publish_attributes_of_a_vthing(vthingindex, attributes):
    # create a ngsild entity with id and type extracted from the vthingindex
    # and with properties (or relationships) coming from the given
    # list of attributes.
    # each item of the list is a dict as follows:
    # {attributename:STRING, attributevalue:WHATEVER, isrelationship:BOOL (optional)}
    ngsildentity = { "id": v_things[vthingindex]["ID_LD"], "type": v_things[vthingindex]["type_attr"] }
    for attribute in attributes:
        if "isrelationship" in attribute and attribute["isrelationship"] == True:
            ngsildentity[attribute["attributename"]] = {"type":"Relationship", "object":attribute["attributevalue"]}
        else:
            ngsildentity[attribute["attributename"]] = {"type":"Property", "value":attribute["attributevalue"]}
    if v_things[vthingindex]['jsonld_at_context_field'] is not None:
        ngsildentity['@context']=v_things[vthingindex]['jsonld_at_context_field']
    data = [ngsildentity]
    v_things[vthingindex]['context'].update(data)
    message = { "data": data, "meta": {"vThingID": v_things[vthingindex]['ID']} }  # neutral-format message
    # usual broadcast topic, so that data is sent to all subscribers of this vthing
    topic = v_things[vthingindex]['topic'] + "/" + out_data_suffix
    publish_message_with_data_client(message, topic)


def publish_message_with_data_client(message, topic):
    msg=json.dumps(message)
    #print("Message published to " + topic + "\n" + msg+"\n")
    # publish data to topic
    mqtt_data_client.publish(topic, msg)


def message_to_jres(message):
    # Utility function
    payload = message.payload.decode("utf-8", "ignore")
    #print("Received on topic " + message.topic + ": " + str(payload))
    jres = json.loads(payload.replace("\'", "\""))
    return jres
    
    
def callback_for_mqtt_data_in_vthing(mosq, obj, message):
    executor.submit(processor_for_mqtt_data_in_vthing, message)
def processor_for_mqtt_data_in_vthing(message):
    jres = message_to_jres(message)
    try:
        data = jres["data"]
        meta = jres["meta"]
        vthingindex=meta["vThingID"].split('/')[-1]
        for entity in data:
            id_LD = entity["id"]
            context_entity=find_entity_within_context(vthingindex,id_LD)
            for cmd in context_entity['commands']['value']:
                if cmd in entity:
                    process_actuation_request(vthingindex,entity)
                    continue
    except:
        traceback.print_exc()


def callback_for_mqtt_data_out_upstream_vthing(mosq, obj, message):
    executor.submit(processor_for_mqtt_data_out_upstream_vthing, message)
def processor_for_mqtt_data_out_upstream_vthing(message):
    jres = message_to_jres(message)
    upstream_entities.clear()
    try:
        data = jres["data"]
        for entity in data:
            upstream_entities.append(entity)
    except:
        traceback.print_exc()


def callback_for_mqtt_control_in_vthing(mosq, obj, message):
    executor.submit(processor_for_mqtt_control_in_vthing, message)
def processor_for_mqtt_control_in_vthing(message):
    jres = message_to_jres(message)
    try:
        command_type = jres["command"]
        n=jres["vThingID"].split('/')[-1]
        if command_type == "getContextRequest":
            publish_getContextResponse_command(jres,n)
    except:
        traceback.print_exc()


def callback_for_mqtt_control_in_TV(mosq, obj, message):
    executor.submit(processor_for_mqtt_control_in_TV, message)
def processor_for_mqtt_control_in_TV(message):
    jres = message_to_jres(message)
    try:
        command_type = jres["command"]
        if command_type == "destroyTV":
            destroy_thing_visor(jres)
        elif command_type == "updateTV":
            update_thing_visor(jres)
    except:
        traceback.print_exc()
    return 'invalid command'

def publish_actuation_response_message(vthingindex, cmd_entity, cmd_name, cmd_info, payload, type_of_message):
    try:
        # type_of_message can be "result" or "status"
        pname = cmd_name + "-" + type_of_message #e.g. startdevice-result
        pvalue = cmd_info.copy()
        # lets set either cmd-result or cmd-status field of the actuation workflow
        field = "cmd-" + type_of_message
        pvalue[field] = payload
        ngsiLdEntity = { "id": cmd_entity["id"], "type": cmd_entity['type'], pname: {"type": "Property", "value": pvalue} }
        if v_things[vthingindex]['jsonld_at_context_field'] is not None:
            ngsiLdEntity['@context']=v_things[vthingindex]['jsonld_at_context_field']
        data = [ngsiLdEntity]
        # not updating the vthings context in the actuation because the commands results are ephemeral
        message = { "data": data, "meta": {"vThingID": v_things[vthingindex]['ID']} }  # neutral-format message
        # fallback broadcast topic, so that data is sent to all subscribers of this vthing, in case the
        # unicast cmd-nuri was not set in the received actuation command 
        topic = v_things[vthingindex]['topic'] + "/" + out_data_suffix
        if "cmd-nuri" in cmd_info:
            if cmd_info['cmd-nuri'].startswith("viriot://"):
                topic = cmd_info['cmd-nuri'][len("viriot://"):]
        publish_message_with_data_client(message, topic)
    except:
        traceback.print_exc()


def process_actuation_request(vthingindex,cmd_entity):
    try:
        id_LD = cmd_entity["id"]
        context_entity=find_entity_within_context(vthingindex,id_LD)
        for cmd_name in context_entity['commands']['value']:
            if cmd_name in cmd_entity:
                cmd_info = cmd_entity[cmd_name]['value']
                fname = cmd_name.replace('-','_')
                fname = "on_" + fname
                # get function object via reflection
                f = getattr(thingvisorspecific, fname)
                # i use this form because now the function to be called is in
                # another module that i do not know the name
                #for k, v in list(globals().items()):
                #    print(k + " ;; ")
                #f = globals()[fname]
                if "cmd-qos" in cmd_info:
                    if int(cmd_info['cmd-qos']) == 2:
                        publish_actuation_response_message(vthingindex, cmd_entity, cmd_name, cmd_info, "PENDING", "status")
                future = executor.submit(f, vthingindex, cmd_entity, cmd_name, cmd_info)
                print("processed actuation command with errors: "+f'{future.result()}')
                #f(cmd_name, cmd_info, id_LD)
    except:
        traceback.print_exc()


def publish_getContextResponse_command(jres, vthingindex):
    silo_id = jres["vSiloID"]
    message = {"command": "getContextResponse", "data": v_things[vthingindex]['context'].get_all(), "meta": {"vThingID": v_things[vthingindex]['ID']}}
    mqtt_control_client.publish(v_silo_prefix + "/" + silo_id + "/" + in_control_suffix, json.dumps(message))


def publish_deleteVThing_command(vthingindex):
    msg = {"command": "deleteVThing", "vThingID": v_things[vthingindex]['ID'], "vSiloID": "ALL"}
    mqtt_control_client.publish(v_thing_prefix + "/" + v_things[vthingindex]['ID'] + "/" + out_control_suffix, json.dumps(msg))


def publish_destroyTVAck_command():
    msg = {"command": "destroyTVAck", "thingVisorID": thing_visor_ID}
    mqtt_control_client.publish(tv_control_prefix + "/" + thing_visor_ID + "/" + out_control_suffix, json.dumps(msg))


def destroy_thing_visor(jres):
    db_client.close()
    for n in v_things:
        publish_deleteVThing_command(n)
    publish_destroyTVAck_command()
    print("Shutdown completed")


def update_thing_visor(jres):
    print("Update received:", jres['params'])
    for key in jres['params']:
        params[key] = jres['params'][key]
        print("  param " + key + " updated to " + str(params[key]))
        if key == "upstream_vthingid":
            connect_to_upstream_thingvisor()


def connect_to_upstream_thingvisor():
    global upstream_tv_http_service
    SVC_SUFFIX = ".default.svc.cluster.local"
    print("parsed upstream_vthingid parameter: " + str(params['upstream_vthingid']))
    upstream_tv_id = params['upstream_vthingid'].split('/',1)[0]
    # get stream information from db
    upstream_tvServiceName = db[thing_visor_collection].find_one({"thingVisorID": upstream_tv_id})['serviceName']
    upstream_tv_http_service = upstream_tvServiceName + SVC_SUFFIX
    print("...and found upstream TV service: " + str(upstream_tv_http_service))
    # now subscribe to data coming from upstream vthing
    upstream_topic = v_thing_prefix + "/" + params['upstream_vthingid'] #vThing/camerasensor-tv/sensor
    mqtt_control_client.message_callback_add(upstream_topic + "/" + out_data_suffix, callback_for_mqtt_data_out_upstream_vthing)
    mqtt_control_client.subscribe(upstream_topic + '/' + out_data_suffix)


# main initializer of the TV
def initialize_thingvisor(thingvisor_specific_module_name):
    global v_things
    global command_data
    global tv_control_prefix
    global thing_visor_ID
    global v_silo_prefix
    global v_thing_prefix
    global in_control_suffix
    global out_control_suffix
    global in_data_suffix
    global out_data_suffix
    global mqtt_control_client
    global mqtt_data_client
    global executor
    global params
    global db
    global upstream_entities
    global thing_visor_collection
    global db_client
    global thingvisorspecific

    # lets import the specific functions and bind them into us
    print("importing module: " + thingvisor_specific_module_name)
    thingvisorspecific = import_module(thingvisor_specific_module_name)

    upstream_entities = []

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
        if parameters and not isinstance(parameters, dict):
            # decode as string only if it is not a 'dict' because sometimes it arrives
            # to us as a string, some other times as a dict... Specifically, after a master controller
            # update-thingvisor command, it turns into a dict...
            params = json.loads(parameters)
        else:
            params={}

    except json.decoder.JSONDecodeError:
        print("error on params (JSON) decoding" + "\n")
        exit()
    except Exception as e:
        print("Error: Parameters not found in tv_entry", e)
        exit()
    print("Init-time params: ")
    for key in params:
        print(str(key) + " -> " + str(params[key]))
    

    if 'upstream_vthingid' in params:
        connect_to_upstream_thingvisor()


    port_mapping = db[thing_visor_collection].find_one({"thingVisorID": thing_visor_ID}, {"port": 1, "_id": 0})
    print("port mapping: " + str(port_mapping))

    # mqtt settings
    tv_control_prefix = "TV"  # prefix name for controller communication topic
    v_thing_prefix = "vThing"  # prefix name for virtual Thing data and control topics
    in_control_suffix = "c_in"
    out_control_suffix = "c_out"
    out_data_suffix = "data_out"
    in_data_suffix = "data_in"
    v_silo_prefix = "vSilo"

    mqtt_control_client = mqtt.Client()
    mqtt_control_client.on_connect = subscribe_TV_control_in_topic
    mqtt_control_client.on_disconnect = mqtt_control_reconnect
    mqtt_control_client.connect(MQTT_control_broker_IP, MQTT_control_broker_port, 30)
    mqtt_data_client = mqtt.Client()
    mqtt_data_client.connect(MQTT_data_broker_IP, MQTT_data_broker_port, 30)
    # starting the two threads, each for each mqtt client we have
    print("Entering main MQTT network loop")
    mqtt_data_client.loop_start()
    mqtt_control_client.loop_start()
    print("MQTT network loop started")
    # threadPoolExecutor of default size
    executor = ThreadPoolExecutor()

    # FOR ACTUATION
    # for each command we receive, store the command information BL BLA
    # NOTE that the native dict type is inherently thread safe in python, so
    # the two threads can concurrently modify it. Moreover, the dict is global
    # because variables in python have global visibility, unless when you CHANGE
    # it, in that case a NEW, LOCAL variable is created if you don't use the global keyword.
    command_data={}

    v_things={}

