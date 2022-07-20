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

import thingVisor_generic_module as thingvisor
import domus_common_functionality as common

import sys
import traceback
import paho.mqtt.client as mqtt
import sched, time
import logging
import os
import socket
import json
from datetime import datetime
from threading import Thread
from pymongo import MongoClient
from context import Context
from flask import Flask
from flask import request
sys.path.insert(0, 'PyLib/')
logging.basicConfig(format='%(asctime)s: %(message)s', level=logging.INFO)

# Mqtt settings
tv_control_prefix = "TV"  # prefix name for controller communication topic
v_thing_prefix = "vThing"  # prefix name for virtual Thing data and control topics
data_in_suffix = "data_in"
data_out_suffix = "data_out"
control_in_suffix = "c_in"
control_out_suffix = "c_out"
v_silo_prefix = "vSilo"

v_thing_contexts = [
    "https://gitlab.com/sferainnovazione/garminconnect/-/raw/staging/VirIoT_fork/Context/context.jsonld"
    #"https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld"
]

entity_types = ['home_humidity', 'home_temperature']

thing_visor_ID = os.environ["thingVisorID"]
parameters = os.environ["params"]
if parameters:
    try:
        params = json.loads(parameters.replace("'", '"'))
    except json.decoder.JSONDecodeError:
        # TODO manage exception
        logging.info("error on params (JSON) decoding")
        os._exit(1)
    except KeyError:
        logging.info(Exception.with_traceback())
        os._exit(1)
    except Exception as err:
        logging.info("ERROR on params (JSON): {}".format(err))


## METHODS USED TO CONVERT DATA FROM DB IN NGSI-LD ENTITIES


# used to group all the oregon measurements into one single dict easier to model as ngsi-ld entity
# also it splits indoor from outdoors measurements
def group_oregon_measurements(raw):
    group_refined_data = []
    email = raw[0]['email'] # they are all measurements about the same user so the email is the same on the whole data

    rooms = list(set(map(lambda x: x['room'], raw))) # list of strings

    for room in rooms:
        raw_filtered_by_room = list(filter(lambda x: x['room'] == room, raw))

        locations = list(set(map(lambda x: x['location'], raw_filtered_by_room))) # contains either ['indoor','outdoor'] or ['indoor'] or ['outdoor']

        for location in locations:
            refined_data = dict()
            raw_filtered_by_location = list(filter(lambda x: x['location'] == location, raw_filtered_by_room))
            #sorting to assure they are all ordered by startTimeInSeconds
            raw_filtered_by_location.sort(key=lambda measure: measure['startTimeInSeconds'])
            
            refined_data['email'] = email
            refined_data['location'] = location
            refined_data['room'] = room

            # we can assume that the information about the mac_address that we have 
            # here comes from the same sensor since we narrowed down both the room and the location
            refined_data['mac_address'] = raw_filtered_by_location[0]['mac_address'].replace(":","")

            firstStartTime = int(raw_filtered_by_location[0]['startTimeInSeconds'])
            lastStartTime = int(raw_filtered_by_location[-1]['startTimeInSeconds'])

            refined_data['startTimeInSeconds'] = firstStartTime
            #durationtInSeconds is calculated by last - first and adding the last duration (which is the same for the first when len=1)
            refined_data['frequencyInSeconds'] = int(raw_filtered_by_location[0]['frequencyInSeconds'])
            refined_data['endTimeInSeconds'] = lastStartTime + int(raw_filtered_by_location[-1]['frequencyInSeconds'])
            refined_data['dataMap'] = dict()

            #creating the map of values
            for raw_data in raw_filtered_by_location:
                offset = str(int(raw_data['startTimeInSeconds']) - firstStartTime)
                refined_data['dataMap'][offset] = raw_data['value']

            group_refined_data.append(refined_data)
    return group_refined_data


#
def create_oregon_entity(raw_measurements, v_thing_type):
    entities = []
    grouped_refined_measurements = group_oregon_measurements(raw_measurements)
    for refined_measurements in grouped_refined_measurements:
        entity = {"@context": v_thing_contexts, "id": "urn:ngsi-ld:{}:{}:{}:{}:{}".format(thing_visor_ID, v_thing_type, refined_measurements['email'],refined_measurements['room'],refined_measurements['location']),"type": v_thing_type} #urn:ngsi-ld:tv-name:(sensor):(email):(room):(indoor|outdoor)
        entity['userEmail'] = {"type": 'Property', 'value': refined_measurements['email']}
        entity['startTimeInSeconds'] = {"type": 'Property', 'value': refined_measurements['startTimeInSeconds']}
        entity['endTimeInSeconds'] = {"type": 'Property', 'value': refined_measurements['endTimeInSeconds']}
        entity['frequencyInSeconds'] = {"type": 'Property', 'value': refined_measurements['frequencyInSeconds']}
        if v_thing_type == 'home_temperature':
            entity['temperatureCelsiusOffsetMap'] = {'type': 'Property', 'value': refined_measurements['dataMap']}
        else:
            entity['humidityPercentageOffsetMap'] = {'type': 'Property', 'value': refined_measurements['dataMap']}
        entity['room'] = {"type": 'Property', 'value': refined_measurements['room']}
        entity['isIndoor'] = {"type": 'Property', 'value': refined_measurements['location'] == "indoor"}
        entity['measuredBySensor'] = {'type': 'Relationship', 'object': "urn:ngsi-ld:{}:sensors:{}".format(thing_visor_ID, refined_measurements['mac_address'])}
        entities.append(entity)
    return entities


def create_sensors_context_entities(sensors_data):
    entities = []
    for sensor_data in sensors_data:
        last_id_value = sensor_data['mac_address'].replace(":","").upper()
        entity=common.create_sensor_context_entity(sensor_data,last_id_value)

        #adding this custom property only for sensors of this specific thingvisor
        entity['frequencyInSeconds'] = {"type": 'Property', 'value': sensor_data['frequencyInSeconds']}

        entities.append(entity)
    return entities

def create_entities(filtered_data, v_thing_type):
    if v_thing_type == "sensors":
        entities = create_sensors_context_entities(filtered_data)
        return entities
    else:
        entities = create_oregon_entity(filtered_data, v_thing_type)
        return entities


def create_datatypes_empty_entities(emails,map_emails_rooms):
    for type in entity_types:
        entities = []

        #setting the entity for each patient
        for el in map_emails_rooms:
            id_LD = "urn:ngsi-ld:" + thing_visor_ID + ":" + type + ":" + el['email'] + ":" + el['room'] + ':'
            ngsiLdEntityIndoor = {
                '@context': v_thing_contexts,
                'id': id_LD + "indoor",
                'type': type,
                'email': {
                    'type': 'Property',
                    'value': el['email']
                },
                'commands': {
                    'type': 'Property',
                    'value': ['query']
                }
            }
            ngsiLdEntityOutdoor = {
                '@context': v_thing_contexts,
                'id': id_LD + 'outdoor',
                'type': type,
                'email': {
                    'type': 'Property',
                    'value': el['email']
                },
                'commands': {
                    'type': 'Property',
                    'value': ['query']
                }
            }
            entities.append(ngsiLdEntityIndoor)
            entities.append(ngsiLdEntityOutdoor)
        thingvisor.v_things[type]['context'].update(entities)


def create_sensors_empty_entities(sensors_data):
    entities = []
    #setting the entity for each sensor stored in the database
    for sensor_data in sensors_data:
        mac_address = sensor_data['mac_address'].replace(":","").upper()
        entity = {"@context": v_thing_contexts, "id": "urn:ngsi-ld:{}:sensors:{}".format(thing_visor_ID, mac_address),"type": "sensor"} #urn:ngsi-ld:tv-name:sensors:(last_id_value)
        entity['owner'] = {"type": 'Property', 'value': sensor_data['owner'] if 'owner' in sensor_data else "-"}
        entity['email'] = {"type": 'Property', 'value': sensor_data['email'] if 'email' in sensor_data else "-"}
        entity['geoPosition'] = {"type": 'Property', 'value': sensor_data['geoPosition'] if 'geoPosition' in sensor_data else "-"}
        entity['status'] = {"type": 'Property', 'value': sensor_data['status'] if 'status' in sensor_data else 0}
        entity['address'] = {"type": 'Property', 'value': sensor_data['address'] if 'address' in sensor_data else "-"}
        entity['frequencyInSeconds'] = {"type": 'Property', 'value': sensor_data['frequency_in_seconds']}
        entity['commands'] = {"type": 'Property', 'value': ['set_frequencyInSeconds']}
        entities.append(entity)
    thingvisor.v_things['sensors']['context'].update(entities)


def on_query(vThingID, cmd_entity, cmd_name, cmd_info):
    common.on_query(vThingID, cmd_entity, cmd_name, cmd_info)

def on_set_frequencyInSeconds(vThingID, cmd_entity, cmd_name, cmd_info):
    try:
        data = 0
        id_LD=cmd_entity['id']
        topic = common.removeViriot(cmd_info['cmd-nuri'])

        if id_LD == "urn:ngsi-ld:" + thing_visor_ID + ":sensors":
            data = "{}".format(time.time())
        else:
            # logging.info("{}".format(cmd_info))
            mac_address = id_LD.split(":")[-1] #last element of the id_LD is the mac address of the sensor
            mac_address_with_colons = ':'.join(mac_address[i:i+2] for i in range(0, len(mac_address), 2)) #needed because the mac_address from the id_LD doesn't have the ":"
            payload = {
                "params": {
                    "is_actuation": True,
                    "mac": mac_address_with_colons,
                    "config": {
                        "new_frequency_in_seconds": int(cmd_info['cmd-value']['new_frequency_in_seconds'])
                    }
                }
            }
            data = common.send_request_to_backend_and_fix("POST", "api/oregon/sensors/config", json=payload)
            #data = "{}".format(time.time())

        thingvisor.publish_actuation_response_message(vThingID, cmd_entity, cmd_name, cmd_info, {"code": "OK", "data": data}, "result")
    except:
        traceback.print_exc()
        thingvisor.publish_actuation_response_message(vThingID, cmd_entity, cmd_name, cmd_info, {"code": "ERROR"}, "result")

# main
if __name__ == '__main__':
    thingvisor.initialize_thingvisor("thingVisor_homethermometer")
    common.initialize(v_thing_contexts,entity_types,'oregon/queryMeasurements',create_entities)

    #creating all the vthings
    emails = common.get_all_patients_emails()
    map_emails_rooms = common.get_map_emails_rooms()
    sensors_data = common.get_sensors_data("api/oregon/sensors/getAll")
    common.create_datatypes_vthings(emails)
    common.create_patients_vthing(emails)
    common.create_sensors_vthing()
    create_datatypes_empty_entities(emails,map_emails_rooms)
    create_sensors_empty_entities(sensors_data)
    common.retrieve_latest_data_sensors(emails)
    print("All vthings initialized")

    common.start_rx_thread()

    time.sleep(2)
    while True:
        try:
            time.sleep(3)
        except:
            logging.info("KeyboardInterrupt")
            time.sleep(1)
            os._exit(1)
