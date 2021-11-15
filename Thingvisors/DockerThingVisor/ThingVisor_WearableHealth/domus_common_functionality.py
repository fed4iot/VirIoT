import thingVisor_generic_module as thingvisor

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
import requests
import copy

# Mqtt settings
tv_control_prefix = "TV"  # prefix name for controller communication topic
v_thing_prefix = "vThing"  # prefix name for virtual Thing data and control topics
data_in_suffix = "data_in"
data_out_suffix = "data_out"
control_in_suffix = "c_in"
control_out_suffix = "c_out"
v_silo_prefix = "vSilo"

# Backend variables
backend_uri = None
backend_port = None

# Login Variables
login_username = ""
login_password = ""

app = Flask(__name__)
flask_port = 8089

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

if 'backendUri' in params.keys():
    backend_uri = params['backendUri']
if 'backendPort' in params.keys():
    backend_port = params['backendPort']
if 'username' in params.keys():
    login_username = params['username']
if 'password' in params.keys():
    login_password = params['password']



#used to refresh the token when needed
def get_token():
    payload = {'username': login_username, 'password': login_password}
    endpoint = 'user/login'
    r = requests.post('{}:{}/{}'.format(backend_uri, backend_port, endpoint), json=payload)
    logging.debug('{}, token refreshed'.format(r.status_code))
    return r.json()["payload"]

def send_request_to_backend(method, endpoint, params={}, token = None):
    try:
        if token is None:
            token = get_token()
        h = {'Authorization': 'Bearer ' + token}
        r = requests.request(method,'{}:{}/{}'.format(backend_uri, backend_port, endpoint), headers=h, params=params)
        return r
    except Exception as err:
        logging.debug('An error occured: {}'.format(err))
        return None

def send_request_to_backend_and_fix(method, endpoint, params={}, token = None):
    r=send_request_to_backend(method, endpoint, params, token)
    if r is None:
        return []
    if r.status_code>=400:
        return []
    return r.json()

def send_query_to_backend(data, token_oauth):
    params = {}
    if "data_type" in data:
        params['data_type'] = data['data_type']

    if "email" in data and data['email'] != None:
        params['email'] = data['email']

    if "date" in data and data['date'] != None:
        params['date'] = data['date']

    if "interval" in data and data['interval'] != None:
        params['interval'] = data['interval']

    if params['data_type'] in ['home_humidity','home_temperature']:
        endpoint = 'oregon/queryMeasurements'
    else:
        endpoint = 'summary/querySummaryMeasurements'

    return send_request_to_backend_and_fix('GET',endpoint,params,token_oauth)

##used to get all the patients emails
def get_all_patients_emails():
    r = send_request_to_backend_and_fix('GET','api/private/user/getPatientsEmails')
    emails = [el['email'] for el in r if el['email']]
    logging.debug("Retrieved this email list: {}".format(emails))
    return emails

##used to get all the patients emails
def get_map_emails_rooms():
    map_emails_rooms = send_request_to_backend_and_fix('GET','api/oregon/sensors/mapEmailRooms')
    logging.debug("Retrieved this map email-room: {}".format(map_emails_rooms))
    return map_emails_rooms

def create_sensor_context_entity(sensor_data,last_id_value):
    entity = {"@context": v_thing_contexts, "id": "urn:ngsi-ld:{}:sensors:{}".format(thing_visor_ID, last_id_value),"type": "sensor"} #urn:ngsi-ld:tv-name:sensors:(last_id_value)
    entity['owner'] = {"type": 'Property', 'value': sensor_data['owner']}
    entity['email'] = {"type": 'Property', 'value': sensor_data['email']}
    entity['geoPosition'] = {"type": 'Property', 'value': sensor_data['geoPosition']}
    entity['status'] = {"type": 'Property', 'value': sensor_data['status']}
    entity['address'] = {"type": 'Property', 'value': sensor_data['address']}
    return entity


def update_meta_entity(emails_list, v_thing_type, query_timestamp):
    id_LD = 'urn:ngsi-ld:' + thing_visor_ID + ':' + v_thing_type
    now = int(time.time())
    entity = {
        '@context': v_thing_contexts,
        'id': id_LD,
        'type': v_thing_type+"-meta",
        'userListWithNewData': {
            'type': 'Property',
            'value': [email for email in emails_list]
        },
        'createdAtTimestamp': {
            "type": "Property",
            "value": now
        },
        'queryDate': {
            "type": "Property",
            "value": now if query_timestamp == None else query_timestamp
        },
        'isLatest': {
            "type": "Property",
            "value": "True" if query_timestamp == None else "False"
        }
    }
    return entity


def publish_entities(entitiesList, topic, v_thing_ID):
    # clear entities list, removing commands
    entitiesList=copy.deepcopy(entitiesList)
    for entity in entitiesList:
        if 'commands' in entity:
            del entity['commands']

    message = {"data": entitiesList, "meta": {"vThingID": v_thing_ID}}
    logging.debug("Publishing data with topic name: {} ,message dimension in B: {}\n\n".format(topic,len(json.dumps(message))))
    # #DEBUG
    # url_endpoint = "http://49c1c7610209.ngrok.io/relay/" + topic
    # payload = {
    #     "data": entitiesList,
    #     "meta": {"vThingID": v_thing_ID}
    # }
    # resp = requests.post(url_endpoint, json=payload)
    thingvisor.publish_message_with_data_client(message,topic)
    return


#this method cretes the entities and then send them in the MQTT system
def create_entities_and_send(data_measurements, data_type, query_timestamp=None, cmd_nuri=None):
    if data_measurements == None:
        logging.debug("create_entities_and_send: Data is empty!")
        return 0
    #this allows us to have as many vThing as the endpoints
    identifier = thing_visor_ID + "/" + data_type #used to pick the right context
    if cmd_nuri == None: #when it is not none it means we are sending to a particular vSilo which asked for data (actuator commands)
        topic = v_thing_prefix + "/" + identifier + "/" + data_out_suffix #topic used by Silos to add the vThing
    else:
        topic = cmd_nuri
    v_thing_ID = thing_visor_ID + "/" + data_type # e.g. tv-name/home_temperature

    ngsi_LD_entity_list = make_entities_list(data_type, data_measurements, query_timestamp, cmd_nuri)

    publish_entities(ngsi_LD_entity_list, topic, v_thing_ID) 
    if len(ngsi_LD_entity_list) > 0:   
        return len(ngsi_LD_entity_list) - 1 # -1 because we don't count the meta-entity update
    else:
        return 0 #it's empty when nothing happened


def make_entities_list(data_type, data_measurements, query_timestamp = None, cmd_nuri = None):
    identifier = data_type #used to pick the right context
    #it will return a list of entities
    ngsi_LD_entity_list, emails_list = make_ngsi_ld_entity_by_emails(data_type, data_measurements)

    now = int(time.time())
    for entity in ngsi_LD_entity_list:
        logging.debug("Sending entity with this id: {}".format(entity['id']))
        entity['createdAtTimestamp'] = {
            "type": "Property",
            "value": now
        }
        entity['queryDate'] = {
            "type": "Property",
            "value": now if query_timestamp == None else query_timestamp
        }
        entity['isLatest'] = {
            "type": "Property",
            "value": "True" if query_timestamp == None else "False"
        }
    if data_type in entity_types:
        meta_entity = update_meta_entity(emails_list, data_type, query_timestamp)
        ngsi_LD_entity_list.append(meta_entity)

    if cmd_nuri == None: #not an actuation command, but latest data so we update the context
        thingvisor.v_things[identifier]['context'].update(ngsi_LD_entity_list)
    
    return ngsi_LD_entity_list


#this method build one single entity for each email grouping data even when they come from different summaryIDs
def make_ngsi_ld_entity_by_emails(v_thing_type, data):
    ngsi_LD_entities = []
    emails = list(set(map(lambda e: e['email'], data))) #list of distinct email in this group of measurements
    emails.sort()

    for email in emails:
        try:
            filtered_data = list(filter(lambda e: e['email'] == email, data)) #list of measurements with the same email
            if 'startTimeInSeconds' in filtered_data[0]:
                filtered_data.sort(key=lambda measure: measure['startTimeInSeconds'])
            entities = create_entities_function(filtered_data, v_thing_type)
            ngsi_LD_entities += entities
        except ValueError as err:
            logging.debug("ERROR make_ngsi_ld_entity_by_emails: {}".format(err))
    return ngsi_LD_entities, emails

def context_latest_data(data_type, email, topic):
    identifier = thing_visor_ID + "/" + data_type
    contextMap = thingvisor.v_things[data_type]['context'].get_all()
    if len(email) > 0:
        for entity in contextMap:
            if email == entity['id'].split(":")[4]: #since the email is the 4th thing in the id -> urn:ngsi-ld:<tv>:<type>:<email>
                publish_entities([entity], topic, identifier)
                return 1
        return 0 #which means it doesn't have any
    else:
        publish_entities(contextMap, topic, identifier)
        return len(contextMap)


def create_patients_vthing(emails):
    thing = 'patients'
    #v_things[v_thing_ID] = {"vThing": {"label": label, "id": v_thing_ID, "description": },
    #                         "topic": topic, "type": ,
    #                         "dataType": 'patients', "thing": thing}

    thingvisor.initialize_vthing(thing,'patients',"Few data about the patients",['query'],v_thing_contexts)

    thingvisor.publish_attributes_of_a_vthing(thing,
                [{
                "attributename" : "listPatientsEmails",
                "attributevalue" : emails
                },{
                "attributename" : "numberOfPatients",
                "attributevalue" : len(emails)
                }])

    entities = create_patients_context_entities(emails)
    thingvisor.v_things[thing]['context'].update(entities)
    return

def create_sensors_vthing():
    thingvisor.initialize_vthing('sensors','sensors',"Few data about the sensors",[],v_thing_contexts)

def create_patients_context_entities(emails):
    entities = []

    #setting the entity for each patient
    for email in emails:
        id_LD = "urn:ngsi-ld:" + thing_visor_ID + ":patients:" + email
        ngsiLdEntity = {
            '@context': v_thing_contexts,
            'id': id_LD,
            'type': 'patients',
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
    return entities


def retrieve_latest_data_sensors(emails):
    try:
        token_oauth = get_token()
        for type in entity_types:
            params = {
                "data_type": type
            }
            r = send_query_to_backend(params, token_oauth)
            if r['data'] != None:
                make_entities_list(type, r['data'])
            time.sleep(0.25)
    except Exception as err:
        logging.debug('An error occured: {}'.format(err))


def retrievePatientMeasurement(cmd_info, data_type, email, topic):
    logging.debug("RetrievePatientMeasurement: {}".format(cmd_info))
    params = {
        "email": email,
        "data_type": data_type
    }
    num_records_queried = 0
    if('cmd-value' in cmd_info):
        if 'date' in cmd_info['cmd-value']:
            date = cmd_info['cmd-value']['date']
        else:
            date = 'latest'

        if 'hoursInterval' in cmd_info['cmd-value']:
            interval = cmd_info['cmd-value']['hoursInterval']
        else:
            interval = 24 #hours

        if date != 'latest' and type(date) == int and date > 0:
            params['date'] = date
            params['interval'] = interval
            token_oauth = get_token()
            r = send_query_to_backend(params, token_oauth)
            if r['data'] != None:
                num_records_queried = create_entities_and_send(r['data'],data_type,date,topic)
        elif date == 'latest':
                num_records_queried = context_latest_data(data_type, email, topic)
    return num_records_queried


def retrievePatientsData():
    # not implemented: patients data never change
    return


def create_datatypes_vthings(emails):
    for type in entity_types:
        thingvisor.initialize_vthing(str(type),type + "-meta",'Sensor which measures ' + str(type),['query'],v_thing_contexts)


def removeViriot(string):
    if string.startswith("viriot://"):
        string = string[len("viriot://"):]
    return string


def on_query(vThingID, cmd_entity, cmd_name, cmd_info):
    try:
        data = 0
        id_LD=cmd_entity['id']
        topic = removeViriot(cmd_info['cmd-nuri'])

        if vThingID in entity_types:
            if id_LD == "urn:ngsi-ld:" + thing_visor_ID + ":" + vThingID:
                email = "" #this way it will get all the patients
                data += retrievePatientMeasurement(cmd_info, vThingID, email, topic)
            elif len(id_LD.split(":")) > 4: #means we have at least the emails
                email = id_LD.split(":")[4] #mails are always 5h
                data += retrievePatientMeasurement(cmd_info, vThingID, email, topic)
        elif vThingID == 'patients':
            if id_LD == "urn:ngsi-ld:" + thing_visor_ID + ":" + vThingID: 
                data = 1
                retrievePatientsData()
            elif len(id_LD.split(":")) == 5:
                email = id_LD.split(":")[4]
                for data_type in entity_types:
                    data += retrievePatientMeasurement(cmd_info, data_type, email, topic)

        thingvisor.publish_actuation_response_message(vThingID, cmd_entity, cmd_name, cmd_info, {"code": "OK", "data": data}, "result")
    except:
        traceback.print_exc()
        thingvisor.publish_actuation_response_message(vThingID, cmd_entity, cmd_name, cmd_info, {"code": "ERROR"}, "result")


## INITIALIZE FUNCTION

def initialize(_v_thing_contexts, _entity_types,_endpoint, _create_entities_function):
    global v_thing_contexts
    global entity_types
    global endpoint
    global create_entities_function
    global data_endpoints
    v_thing_contexts=_v_thing_contexts
    entity_types=_entity_types
    endpoint=_endpoint
    create_entities_function=_create_entities_function
    data_endpoints=_entity_types.copy()
    data_endpoints.append('sensor')

## FLASK THREAD CLASS


def start_rx_thread():
    rxThread = httpRxThread()  # http server used to receive JSON messages from external producer
    rxThread.start()


class httpRxThread(Thread):
    def __init__(self):
        Thread.__init__(self)

    def run(self):
        global app

        logging.debug("Thread Rx HTTP started")
        app.run(host='0.0.0.0', port=flask_port)
        logging.debug("Thread {} closed".format(self.name))


@app.route('/<string:endpoint>', methods=['POST'])
def recv_notify(endpoint):
    try:
        if endpoint not in data_endpoints:
            raise ValueError('Only accepted routes are ', data_endpoints)
        jres = request.get_json(force=True)

        
        create_entities_and_send(jres, endpoint)
        
        return 'OK', 201
    except ValueError as err:
        logging.debug('Requested URL /{} was not found in this server. {}'.format(endpoint, err))
        return 'Requested URL /{} was not found in this server'.format(endpoint), 404

@app.route('/query', methods=['GET'])
def send_get_message():
    try:
        if request.args.get('data_type') not in data_endpoints:
            raise ValueError('Only accepted data types are ', data_endpoints)
        params = {}
        params['data_type'] = request.args.get('data_type')
        params['email'] = request.args.get('email')
        params['date'] = request.args.get('date')
        token_oauth = get_token()
        r = send_query_to_backend(params, token_oauth)
        if r['data'] != None:
            create_entities_and_send(r['data'],params['data_type'])
        logging.debug('OK httpRxThread /query: 222')
        return r
    except ValueError as err:
        logging.debug("ERROR httpRxThread /query: {}".format(err))
        return 'Error', 404

@app.route('/getContext', methods=['GET'])
def retrieve_context_data():
    try:
        if request.args.get('data_type') not in data_endpoints:
            raise ValueError('Only accepted data types are ', data_endpoints)
        identifier = request.args.get('data_type')
        contextMap = thingvisor.v_things[identifier]['context'].get_all()
        r = dict()
        if 'entity_id' in request.args:
            entity_id = request.args.get('entity_id')
            #logging.debug(entity_id)
            if entity_id is not None:
                r['data'] = list(filter(lambda entity: entity['id'] == entity_id, contextMap))
            else:
                r['data'] = []
        else:
            r['data'] = contextMap
        logging.debug('OK httpRxThread /getContext: 202')
        return r
    except ValueError as err:
        logging.debug("ERROR httpRxThread /getContext: {}".format(err))
        return 'Error', 404
