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

entity_types = ['heart_rate', 'pulse_ox', 'light_sleep', 'deep_sleep', 'rem_sleep', 'awake_periods', 'motion_intensity']

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

# offset in seconds
filter_heart_rate_offset = 0
filter_pulse_ox_offset = 0

if "filter_heart_rate_offset" in params:
    filter_heart_rate_offset = params["filter_heart_rate_offset"]
if "filter_pulse_ox_offset" in params:
    filter_pulse_ox_offset = params["filter_pulse_ox_offset"]


## METHODS USED TO CONVERT DATA FROM DB IN NGSI-LD ENTITIES

map_prop_names = {  
    'pulse_ox' : {"map_name": 'timeOffsetSleepSpo2'},
    'heart_rate' : {"map_name": 'timeOffsetHeartRateSamples'},
    'rem_sleep' : {"map_name": 'remSleepMap', "prop_name": 'remSleepInSeconds'},
    'light_sleep' : {"map_name": 'lightSleepMap', "prop_name": 'lightSleepInSeconds'},
    'deep_sleep' : {"map_name": 'deepSleepMap', "prop_name": 'deepSleepInSeconds'},
    'awake_periods' : {"map_name": 'awakeMap', "prop_name": 'awakeInSeconds'}
}

#used to group all the properties for motion intensity into a single object
def group_motion_intensity_measurements(raw):
    refined_data = dict()

    #sorting to assure they are all ordered by startTimeInSeconds
    raw.sort(key=lambda measure: measure['startTimeInSeconds'])
    
    refined_data['email'] = raw[0]['email']
    firstStartTime = int(raw[0]['startTimeInSeconds'])
    lastStartTime = int(raw[-1]['startTimeInSeconds'])

    refined_data['startTimeInSeconds'] = firstStartTime
    #durationtInSeconds is calculated by last - first and adding the last duration (which is the same for the first when len=1)
    refined_data['durationInSeconds'] = lastStartTime - firstStartTime + int(raw[-1]['durationInSeconds']) #should be a multiple of 15 min
    refined_data['endTimeInSeconds'] = lastStartTime + int(raw[-1]['durationInSeconds'])

    refined_data['meanMotionIntensity'] = dict()
    refined_data['maxMotionIntensity'] = dict()
    refined_data['intensity'] = dict()
    refined_data['distanceInMeters'] = dict()
    refined_data['steps'] = dict()
    refined_data['activityType'] = dict()

    #creating the map of values
    for raw_data in raw:
        offset = str(int(raw_data['startTimeInSeconds']) - firstStartTime)
        refined_data['meanMotionIntensity'][offset] = float(raw_data['mean_motion_intensity'])
        refined_data['maxMotionIntensity'][offset] = float(raw_data['max_motion_intensity'])
        refined_data['intensity'][offset] = raw_data['intensity']
        refined_data['distanceInMeters'][offset] = int(raw_data['distance_in_meters'])
        refined_data['steps'][offset] = int(raw_data['steps'])
        refined_data['activityType'][offset] = raw_data['activity_type']

    return refined_data


def create_motion_intensity_entity(raw_measurements):
    refined_measurements = group_motion_intensity_measurements(raw_measurements)
    entity = {"@context": v_thing_contexts, "id": "urn:ngsi-ld:{}:motion_intensity:{}".format(thing_visor_ID,refined_measurements['email']),"type": "motion_intensity"} #urn:ngsi-ld:tv-name:motion_intensity:(email)
    entity['userEmail'] = {"type": 'Property', 'value': refined_measurements['email']}
    entity['startTimeInSeconds'] = {"type": 'Property', 'value': refined_measurements['startTimeInSeconds']}
    entity['endTimeInSeconds'] = {"type": 'Property', 'value': refined_measurements['endTimeInSeconds']}
    entity['durationInSeconds'] = {"type": 'Property', 'value': refined_measurements['durationInSeconds']}
    entity['meanMotionIntensity'] = {'type': 'Property', 'value': refined_measurements['meanMotionIntensity']}
    entity['maxMotionIntensity'] = {'type': 'Property', 'value': refined_measurements['maxMotionIntensity']}
    entity['intensity'] = {'type': 'Property', 'value': refined_measurements['intensity']}
    entity['distanceInMeters'] = {'type': 'Property', 'value': refined_measurements['distanceInMeters']}
    entity['steps'] = {'type': 'Property', 'value': refined_measurements['steps']}
    entity['activityType'] = {'type': 'Property', 'value': refined_measurements['activityType']}
    entity['measuredBySensor'] = {'type': 'Relationship', 'object': "urn:ngsi-ld:{}:sensors:{}".format(thing_visor_ID, refined_measurements['email'])}
    return entity


def perform_filter_operation(data_to_be_filtered, params_offset):
    filtered_data = [data_to_be_filtered[0]]
    startTimeInSeconds = int(data_to_be_filtered[0]["startTimeInSeconds"])
    offset = int(list(data_to_be_filtered[0]["value"].keys())[0]) # we can do it because these measurements have exactly one item
    last_timestamp = startTimeInSeconds + offset
    i = 1
    while i < len(data_to_be_filtered):
        startTimeInSeconds = int(data_to_be_filtered[i]["startTimeInSeconds"])
        offset = int(list(data_to_be_filtered[i]["value"].keys())[0]) # we can do it because these measurements have exactly one item
        current_timestamp = startTimeInSeconds + offset
        # If the delta between timestamp of the current measurement
        # and the last one added in filtered_data is greater than the params_offset
        # we can add this measurement inside filtered_data
        if current_timestamp - last_timestamp >= params_offset:
            last_timestamp = current_timestamp
            filtered_data.append(data_to_be_filtered[i])
        i+=1
    return filtered_data

# This method is called to filter heart_rate and pulse_ox measurements based on the parameters 
# filter_heart_rate_offset and filter_pulse_ox_offset that could have been passed when the
# the thingvisor was created. It returns the data filtered if those values are more than 0.
def filter_measurements_from_offset(data_type, raw_data):
    data = raw_data.copy()
    if data_type == "heart_rate":
        if filter_heart_rate_offset > 0:
            data = perform_filter_operation(data, filter_heart_rate_offset)
    else: # data_type == pulse_ox
        if filter_pulse_ox_offset > 0:
            data = perform_filter_operation(data, filter_pulse_ox_offset)
    return data


#used to group all the properties into a single object. Used for every vthing except motion_intensity
def group_measurements(raw, v_thing_type):
    refined_data = dict()

    #sorting to assure they are all ordered by startTimeInSeconds
    raw.sort(key=lambda measure: measure['startTimeInSeconds'])
    if v_thing_type in ['heart_rate', 'pulse_ox']:
        raw = filter_measurements_from_offset(v_thing_type, raw)
    #print(raw)
    
    refined_data['email'] = raw[0]['email']
    firstStartTime = int(raw[0]['startTimeInSeconds'])
    lastStartTime = int(raw[-1]['startTimeInSeconds'])

    refined_data['startTimeInSeconds'] = firstStartTime
    #durationtInSeconds is calculated by last - first and adding the last duration (which is the same for the first when len=1)
    refined_data['durationInSeconds'] = lastStartTime - firstStartTime + int(raw[-1]['durationInSeconds'])
    refined_data['endTimeInSeconds'] = lastStartTime + int(raw[-1]['durationInSeconds'])

    #this helps initializing exactly the data we need for the different vthings we have
    if v_thing_type in ['heart_rate', 'pulse_ox']:
        refined_data[map_prop_names[v_thing_type]['map_name']] = dict()
    else:
        unique_summary_ids = list({v['summary_id']:v for v in raw}.values()) #getting the unique dicts
        sleep_prop = map_prop_names[v_thing_type]['prop_name'] #renaming the variable cleaner to read
        map_name = map_prop_names[v_thing_type]['map_name'] #renaming the variable cleaner to read

        # this is the sum of all the actual durations of light_sleep/rem/etc
        refined_data[sleep_prop] = sum([int(x[sleep_prop]) for x in unique_summary_ids])
        refined_data[map_name] = [] #initializing this property as empty list

    #creating the map of values
    for raw_data in raw:
        rawStartTime = int(raw_data['startTimeInSeconds'])
        offset = rawStartTime - firstStartTime
        map_name = map_prop_names[v_thing_type]['map_name'] #renaming the variable cleaner to read. It is the map name inside the raw_data which differs from vthing to vthing
        if v_thing_type in ['heart_rate', 'pulse_ox']:
            key = int(list(raw_data['value'].keys())[0]) #they all have one only key which is used as offset
            refined_data[map_name][str(offset + key)] = int(raw_data['value'][str(key)])
        else:
            refined_data[map_name].append({
                'startTimeInSeconds': int(raw_data['value']['startTimeInSeconds']),
                'endTimeInSeconds': int(raw_data['value']['endTimeInSeconds'])
            })
    return refined_data


def create_entity_from_measurements(raw_measurements, v_thing_type):
    refined_measurements = group_measurements(raw_measurements,v_thing_type)
    entity = {"@context":v_thing_contexts, "id": "urn:ngsi-ld:{}:{}:{}".format(thing_visor_ID, v_thing_type, refined_measurements['email']),"type": v_thing_type} #urn:ngsi-ld:tv-name:(Type):(email)
    #entity = {"@context":v_thing_contexts, "id": "{}".format(v_thing_ID_LD),"type": v_thing_type} #urn:ngsi-ld:tv-name:(Type)
    entity['userEmail'] = {"type": 'Property', 'value': refined_measurements['email']}
    entity['startTimeInSeconds'] = {"type": 'Property', 'value': refined_measurements['startTimeInSeconds']}
    entity['endTimeInSeconds'] = {"type": 'Property', 'value': refined_measurements['endTimeInSeconds']}
    entity['durationInSeconds'] = {"type": 'Property', 'value': refined_measurements['durationInSeconds']}
    entity[ map_prop_names[v_thing_type]['map_name'] ] = {"type": 'Property', 'value': refined_measurements[  map_prop_names[v_thing_type]['map_name'] ] }
    if v_thing_type not in ['heart_rate','pulse_ox']:
        entity[ map_prop_names[v_thing_type]['prop_name'] ] = {'type': 'Property', 'value': refined_measurements[ map_prop_names[v_thing_type]['prop_name'] ]} #sum of each measure
    entity['measuredBySensor'] = {'type': 'Relationship', 'object': "urn:ngsi-ld:{}:sensors:{}".format(thing_visor_ID, refined_measurements['email'])}
    return entity

def create_sensors_context_entities(sensors_data):
    entities = []
    for sensor_data in sensors_data:
        last_id_value = sensor_data['email']
        entity=common.create_sensor_context_entity(sensor_data,last_id_value)
        entities.append(entity)
    return entities

def create_entities(filtered_data, v_thing_type):
    if v_thing_type == "sensors":
        entities = create_sensors_context_entities(filtered_data)
        return entities
    else:
        entity = {}
        if v_thing_type == 'motion_intensity':
            entity = create_motion_intensity_entity(filtered_data)
        else:
            entity = create_entity_from_measurements(filtered_data, v_thing_type)
        return [entity]


def create_datatypes_empty_entities(emails):
    for sensor in entity_types:
        entities = []

        #setting the entity for each patient
        for email in emails:
            id_LD = "urn:ngsi-ld:" + thing_visor_ID + ":" + sensor + ":" + email
            ngsiLdEntity = {
                '@context': v_thing_contexts,
                'id': id_LD,
                'type': sensor,
                'email': {
                    'type': 'Property',
                    'value': email
                },
                'commands': {
                    'type': 'Property',
                    'value': ['query']
                }
            }
            entities.append(ngsiLdEntity)
        thingvisor.v_things[sensor]['context'].update(entities)

def create_sensors_empty_entities(sensors_data):
    entities = []
    #setting the entity for each sensor stored in the database
    for sensor_data in sensors_data:
        entity = {"@context": v_thing_contexts, "id": "urn:ngsi-ld:{}:sensors:{}".format(thing_visor_ID, sensor_data['email']),"type": "sensor"} #urn:ngsi-ld:tv-name:sensors:(last_id_value)
        entity['owner'] = {"type": 'Property', 'value': sensor_data['owner'] if 'owner' in sensor_data else "-"}
        entity['email'] = {"type": 'Property', 'value': sensor_data['email'] if 'email' in sensor_data else "-"}
        entity['geoPosition'] = {"type": 'Property', 'value': sensor_data['geoPosition'] if 'geoPosition' in sensor_data else "-"}
        entity['status'] = {"type": 'Property', 'value': sensor_data['status'] if 'status' in sensor_data else 0}
        entity['address'] = {"type": 'Property', 'value': sensor_data['address'] if 'address' in sensor_data else "-"}
        entities.append(entity)
    thingvisor.v_things['sensors']['context'].update(entities)


def on_query(vThingID, cmd_entity, cmd_name, cmd_info):
    common.on_query(vThingID, cmd_entity, cmd_name, cmd_info)


# main
if __name__ == '__main__':
    thingvisor.initialize_thingvisor("thingVisor_wearablehealth")
    common.initialize(v_thing_contexts,entity_types,'summary/querySummaryMeasurements',create_entities)

    #creating all the vthings
    emails = common.get_all_patients_emails()
    sensors_data = common.get_sensors_data("summary/sensors/getAll")
    common.create_datatypes_vthings(emails)
    common.create_patients_vthing(emails)
    common.create_sensors_vthing()
    create_datatypes_empty_entities(emails)
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
