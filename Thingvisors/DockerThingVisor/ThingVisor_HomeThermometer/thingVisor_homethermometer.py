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
logging.basicConfig(format='%(asctime)s: %(message)s', level=logging.DEBUG)

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
        logging.debug("error on params (JSON) decoding")
        os._exit(1)
    except KeyError:
        logging.debug(Exception.with_traceback())
        os._exit(1)
    except Exception as err:
        logging.debug("ERROR on params (JSON): {}".format(err))


## METHODS USED TO CONVERT DATA FROM DB IN NGSI-LD ENTITIES


#used to group all the oregon measurements into one single dict easier to model as ngsi-ld entity
def group_oregon_measurements(raw):
    refined_data = dict()

    #sorting to assure they are all ordered by startTimeInSeconds
    raw.sort(key=lambda measure: measure['startTimeInSeconds'])
    
    refined_data['email'] = raw[0]['email']
    refined_data['location'] = raw[0]['location']
    refined_data['room'] = raw[0]['room']
    firstStartTime = int(raw[0]['startTimeInSeconds'])
    lastStartTime = int(raw[-1]['startTimeInSeconds'])

    refined_data['startTimeInSeconds'] = firstStartTime
    #durationtInSeconds is calculated by last - first and adding the last duration (which is the same for the first when len=1)
    refined_data['frequencyInSeconds'] = int(raw[0]['frequencyInSeconds'])
    refined_data['endTimeInSeconds'] = lastStartTime + int(raw[-1]['frequencyInSeconds'])
    refined_data['dataMap'] = dict()

    #creating the map of values
    for raw_data in raw:
        offset = str(int(raw_data['startTimeInSeconds']) - firstStartTime)
        refined_data['dataMap'][offset] = raw_data['value']

    return refined_data


#
def create_oregon_entity(raw_measurements, v_thing_type):
    refined_measurements = group_oregon_measurements(raw_measurements)
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
    entity['measuredBySensor'] = {'type': 'Relationship', 'object': "urn:ngsi-ld:sensors:1"}
    return entity


def create_sensors_context_entities(sensors_data):
    entities = []
    for sensor_data in sensors_data:
        last_id_value = sensor_data['mac_address'].replace(":","").upper()
        entity=common.create_sensor_context_entity(sensor_data,last_id_value)
        entities.append(entity)
    return entities

def create_entities(filtered_data, v_thing_type):
    if v_thing_type == "sensor":
        entities = create_sensors_context_entities(filtered_data)
        return entities
    else:
        entity = {}
        entity = create_oregon_entity(filtered_data, v_thing_type)
        return [entity]


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


def on_query(vThingID, cmd_entity, cmd_name, cmd_info):
    common.on_query(vThingID, cmd_entity, cmd_name, cmd_info)



# main
if __name__ == '__main__':
    thingvisor.initialize_thingvisor("thingVisor_homethermometer")
    common.initialize(v_thing_contexts,entity_types,'oregon/queryMeasurements',create_entities)

    #creating all the vthings
    emails = common.get_all_patients_emails()
    map_emails_rooms = common.get_map_emails_rooms()
    common.create_datatypes_vthings(emails)
    common.create_patients_vthing(emails)
    common.create_sensors_vthing()
    create_datatypes_empty_entities(emails,map_emails_rooms)
    common.retrieve_latest_data_sensors(emails)
    print("All vthings initialized")

    common.start_rx_thread()

    time.sleep(2)
    while True:
        try:
            time.sleep(3)
        except:
            logging.debug("KeyboardInterrupt")
            time.sleep(1)
            os._exit(1)
