import sys
import traceback
import paho.mqtt.client as mqtt
import time
import os
import socket
import json
import requests
from threading import Thread
from pymongo import MongoClient
from context import Context
from flask import Flask
#from flask import json
from flask import request
from werkzeug.serving import WSGIRequestHandler

import kafka

# sys.path.insert(0, '/app/PyLib/')
sys.path.insert(0, 'PyLib/')

WSGIRequestHandler.protocol_version = "HTTP/1.1"    # to support keep-alive
#app = Flask(__name__)
#flask_port = 8089

from concurrent.futures import ThreadPoolExecutor

at_context = {'type': 'StructuredValue',
              'value': [
                  'http://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld',
                  'https://fed4iot.nz.comm.waseda.ac.jp/cbpfOntology/v1/cbpf-context.jsonld'
                  ]
             }

### for logger
KAFKA_BROKER = "133.9.250.209:9092"
KAFKA_TOPIC = "fed4iot_tv_logger"
TIMEOUT = 10

kafka_broker = kafka.KafkaProducer(bootstrap_servers=KAFKA_BROKER,
        max_request_size=15728640,api_version_auto_timeout_ms=int(TIMEOUT))
###

#def publish(message):
#    print("topic name: " + v_thing_topic + '/' + data_out_suffix + " ,message: " + json.dumps(message))
#    mqtt_data_client.publish(v_thing_topic + '/' + data_out_suffix,json.dumps(message))

class mqttDataThread(Thread):
    # mqtt client used for sending data
    def __init__(self):
        Thread.__init__(self)

    def run(self):
        print("Thread mqtt data started")

        #commands = ["start", "close"]
        ngsiLdEntity = {"id": v_thing_ID_LD,
                        "type": v_thing_type_attr,
                        "status": {"type": "Property", "value": "close"},
                        "commands": {"type": "Property", "value": commands},
                        "@context": at_context,
                        "msg": "null"
                       }
        
        data =[ngsiLdEntity]
        context_vThing.set_all(data)

        mqtt_data_client.connect(MQTT_data_broker_IP, MQTT_data_broker_port, 30)
        mqtt_data_client.message_callback_add(v_thing_topic + "/" + data_in_suffix,
                                              self.on_message_data_in_vThing)
        mqtt_data_client.subscribe(v_thing_topic + "/" + data_in_suffix)

        ### run publish v_thing thread
        publish_v_thing_thread = Thread(target=self.publish_v_thing)
        publish_v_thing_thread.setDaemon(True)
        publish_v_thing_thread.start()

        mqtt_data_client.loop_forever()


    ### publish v_thing to mqtt broker
    def publish_v_thing(self):
        global context_vThing

        ### get data from camera virtualization system
        API = "/api/get_result"
        end_point = camera_end_point + API

        base_time = time.time()
        next_time = 0
        result = ""

        while True:
            try:

                ts1 = time.time()
                response = requests.get(end_point)
                ts2 = time.time()

                json_response = response.json()

                if (json_response is not None):
                    result = json.loads(json_response)
                else:
                    result = json_response
                pass
            
                if result['msg']['createdAt']['value'] != 'null':
                    ngsiLdEntity1 = result

                    ngsiLdEntity1['@contect'] = at_context
                    ngsiLdEntity1['id'] = v_thing_ID_LD
                    ngsiLdEntity1['type'] = v_thing_type_attr

                    context_vThing.update([ngsiLdEntity1])
                    message = {"data": [ngsiLdEntity1], "meta": {"vThingID": v_thing_ID}}
                    #print("topic name: " + v_thing_topic + '/' + data_out_suffix + " ,message: " + json.dumps(message))

                    ts3 = time.time()
                    mqtt_data_client.publish(v_thing_topic + '/' + data_out_suffix,json.dumps(message))
                    ts4 = time.time()

                    tv_log_info = {"id": v_thing_ID, "type": "data logger", "log": [ts2-ts1, ts4-ts3, ts4-ts1]}
                    kafka_broker.send(KAFKA_TOPIC, json.dumps(tv_log_info).encode('utf-8'))
                    print (tv_log_info)

                else:
                    print ("there is no data")
                    pass

            except requests.exceptions.RequestException as e:
                print ("request error: ", e)

            next_time = ((base_time - time.time()) % request_rate) or request_rate
            time.sleep(next_time)


    def send_commandResult(self, cmd_name, cmd_info, id_LD, result_code):
        pname = cmd_name+"-result"
        pvalue = cmd_info.copy()
        pvalue['cmd-result'] = result_code
        ngsiLdEntityResult = {"id": id_LD,
                                "type": v_thing_type_attr,
                                pname: {"type": "Property", "value": pvalue},
                                "@context": at_context
                                }
        data = [ngsiLdEntityResult]
        # LampActuatorContext.update(data)

        message = {"data": data, "meta": {
                   "vThingID": v_thing_ID}}  # neutral-format message
        if "cmd-nuri" in cmd_info:
            if cmd_info['cmd-nuri'].startswith("viriot://"):
                topic = cmd_info['cmd-nuri'][len("viriot://"):]
                self.publish(message, topic)
            else:
                self.publish(message)
        else:
            self.publish(message)

    def send_commandStatus(self, cmd_name, cmd_info, id_LD, status_code):
        pname = cmd_name+"-status"
        pvalue = cmd_info.copy()
        pvalue['cmd-status'] = status_code
        ngsiLdEntityStatus = {"id": id_LD,
                                "type": v_thing_type_attr,
                                pname: {"type": "Property", "value": pvalue},
                                "@context": at_context
                                }
        data = [ngsiLdEntityStatus]

        message = {"data": data, "meta": {
            "vThingID": v_thing_ID}}  # neutral-format message
        if "cmd-nuri" in cmd_info:
            if cmd_info['cmd-nuri'].startswith("viriot://"):
                topic = cmd_info['cmd-nuri'][len("viriot://"):]
                self.publish(message, topic)
            else:
                self.publish(message)
        else:
            self.publish(message)

    def receive_commandRequest(self, cmd_entity):
        print ("receive_commandRequest")
        try:
            #jsonschema.validate(data, commandRequestSchema)
            id_LD = cmd_entity["id"]
            for cmd_name in commands:
                if cmd_name in cmd_entity:
                    cmd_info = cmd_entity[cmd_name]['value']
                    fname = cmd_name.replace('-','_')
                    fname = "on_"+fname
                    f=getattr(self,fname)
                    if "cmd-qos" in cmd_info:
                        if int(cmd_info['cmd-qos']) == 2:
                            self.send_commandStatus(cmd_name, cmd_info, id_LD, "PENDING")
                    future = executor.submit(f, cmd_name, cmd_info, id_LD, self)


        #except jsonschema.exceptions.ValidationError as e:
            #print("received commandRequest got a schema validation error: ", e)
        #except jsonschema.exceptions.SchemaError as e:
            #print("commandRequest schema not valid:", e)
        except Exception as ex:
            traceback.print_exc()
        return

    ### start camera virtualization system
    def on_start(self, cmd_name, cmd_info, id_LD, actuatorThread):

        _cmd_info = cmd_info

        print ("upload request image")
        cmd_upload = "/upload"
        headers = {'Content-Type': 'application/json'}
        data = cmd_info['cmd-params']

        end_point_up = camera_end_point + "/api" + str(cmd_upload)
        
        try:
            ts1 = time.time()
            response = requests.post(end_point_up, headers=headers, data=json.dumps(data))
            ts2 = time.time()

        except requests.exceptions.RequestException as e:
            print ("request error: ", e)
        print (response)
        print ("upload ok")

        print ("start camera system")
        cmd_start = "/face_rec=start"
        end_point_start = camera_end_point + "/api" + str(cmd_start)
       
        try:
            ts3 = time.time()
            response = requests.get(end_point_start)
            ts4 = time.time()

        except requests.exceptions.RequestException as e:
            print ("request error: ", e)
        print (response)
        print ("start ok")

        tv_log_info = {"id": id_LD, "type": "cmd logger", "log": [(ts2-ts1), (ts4-ts3), (ts4-ts1)]}
        kafka_broker.send(KAFKA_TOPIC, json.dumps(tv_log_info).encode('utf-8'))
        print (tv_log_info)

        # publish command result
        if "cmd-qos" in cmd_info:
            if int(cmd_info['cmd-qos']) > 0:
                _cmd_info.pop('cmd-params')
                self.send_commandResult(cmd_name, _cmd_info, id_LD, "OK")


    ### close camera virtualization system
    def on_close(self, cmd_name, cmd_info, id_LD, actuatorThread):
        
        print ("remove all images")
        cmd_remove = "/remove_img=all"
        end_point_remove = camera_end_point + "/api" + str(cmd_remove)

        try:
            ts1 = time.time()
            response = requests.get(end_point_remove)
            ts2 = time.time()

        except requests.exceptions.RequestException as e:
            print ("request error: ", e)
        print (response)
        print ("remove ok")

        tv_log_info = {"id": id_LD, "type": "cmd logger", "log": [(ts2-ts1)]}
        kafka_broker.send(KAFKA_TOPIC, json.dumps(tv_log_info).encode('utf-8'))
        print (tv_log_info)

        #print ("close camera system")
        #cmd_close = "/face_rec=close"
        #end_point_close = camera_end_point + "/api" + str(cmd_close)

        #try:
        #    response = requests.get(end_point_close)
        
        #except requests.exceptions.RequestException as e:
        #    print ("request error: ", e)
        #print (response)
        #print ("close ok")

        # publish command result
        if "cmd-qos" in cmd_info:
            if int(cmd_info['cmd-qos']) > 0:
                self.send_commandResult(cmd_name, cmd_info, id_LD, "OK")


    def on_set_status(self, cmd_name, cmd_info, id_LD, actuatorThread):
        global context_vThing
        # function to change the status of the Lamp should be written here
        # update the Context, publish new actuator status on data_out, send result
        ngsiLdEntity = {"id": id_LD,
                        "type": v_thing_type_attr,
                        "status": {"type": "Property", "value": cmd_info['cmd-value']},
                        "@context": at_context
                        }
        data = [ngsiLdEntity]
        context_vThing.update(data)

        # publish changed status
        message = {"data": data, "meta": {
            "vThingID": v_thing_ID}}  # neutral-format message
        self.publish(message)

        # publish command result
        if "cmd-qos" in cmd_info:
            if int(cmd_info['cmd-qos']) > 0:
                self.send_commandResult(cmd_name, cmd_info, id_LD, "OK")

    def on_message_data_in_vThing(self, mosq, obj, msg):
        payload = msg.payload.decode("utf-8", "ignore")
        print("Message received on "+msg.topic + "\n" + payload+"\n")
        jres = json.loads(payload.replace("\'", "\""))
        try:
            data = jres["data"]
            for entity in data:
                id_LD = entity["id"]
                if id_LD != v_thing_ID_LD:
                    print("Entity not handled by the Thingvisor, message dropped")
                    continue
                for cmd in commands:
                    if cmd in entity:
                        self.receive_commandRequest(entity)
                        continue
            return
        except Exception as ex:
            traceback.print_exc()
        return

    def publish(self, message, topic=""):
        msg = json.dumps(message)
        if topic == "":
            out_topic = v_thing_topic + '/' + data_out_suffix
        else:
            out_topic = topic

        print("Message sent on " + out_topic + "\n" + msg + "\n")
        mqtt_data_client.publish(out_topic, msg)



'''
class mqttRxThread(Thread):
    # mqtt client used for receiving and sending data
    def __init__(self):
        Thread.__init__(self)

    def on_message_in_rx(self, mosq, obj, msg):
        payload = msg.payload
        # payload = msg.payload.decode("utf-8", "ignore")
        # print("on_message_in_rx ---> msg -->", msg.topic + " " + payload)
        # print("payload --- ", json.loads(payload))
        # print("type payload --- ", type(json.loads(payload)))

        mqtt_VirIoT_client.publish(v_thing_topic + '/' + v_thing_data_out_suffix,
                                 payload=payload)

        
        # silo_id = jres["vSiloID"]
        # message = {"command": "getContextResponse", "data": context_vThing.get_all(), "meta": {"vThingID": v_thing_ID}}
        # mqtt_control_client.publish(v_silo_prefix + "/" + silo_id + "/" + in_control_suffix, str(message).replace("\'", "\""))

    def run(self):
        print("Thread mqtt ribbon started")
        global mqtt_ribbon_client
        mqtt_ribbon_client.connect(MQTT_VirIoT_data_broker_IP, MQTT_VirIoT_data_broker_port, 30)
        # Add message callbacks that will only trigger on a specific subscription match
        mqtt_ribbon_client.message_callback_add("ribbonTopic", self.on_message_in_rx)
        mqtt_ribbon_client.subscribe('ribbonTopic')
        mqtt_ribbon_client.loop_forever()
        print("Thread '" + self.name + "' terminated")

'''

class mqttControlThread(Thread):

    def on_message_get_thing_context(self, jres):
        silo_id = jres["vSiloID"]
        msg = {"command": "getContextResponse", "data": context_vThing.get_all(), "meta": {"vThingID": v_thing_ID}}
        mqtt_control_client.publish(v_silo_prefix + "/" + silo_id + "/" + control_in_suffix, json.dumps(msg))

    def send_destroy_v_thing_message(self):
        msg = {"command": "deleteVThing", "vThingID": v_thing_ID, "vSiloID": "ALL"}
        mqtt_control_client.publish(v_thing_prefix + "/" + v_thing_ID + "/" + control_out_suffix, json.dumps(msg))
        return

    def send_destroy_thing_visor_ack_message(self):
        msg = {"command": "destroyTVAck", "thingVisorID": thing_visor_ID}
        mqtt_control_client.publish(tv_control_prefix + "/" + thing_visor_ID + "/" + control_out_suffix, json.dumps(msg))
        return

    def on_message_destroy_thing_visor(self, jres):
        global db_client
        db_client.close()
        self.send_destroy_v_thing_message()
        self.send_destroy_thing_visor_ack_message()
        print("Shutdown completed")

    # handler for mqtt control topics
    def __init__(self):
        Thread.__init__(self)

    def on_message_in_control_vThing(self, mosq, obj, msg):
        payload = msg.payload.decode("utf-8", "ignore")
        print(msg.topic + " " + str(payload))
        jres = json.loads(payload.replace("\'", "\""))
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
        jres = json.loads(payload.replace("\'", "\""))
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
        mqtt_control_client.publish(tv_control_prefix + "/" + thing_visor_ID + "/" + control_out_suffix,
                                    str(v_thing_message).replace("\'", "\""))

        # Add message callbacks that will only trigger on a specific subscription match
        mqtt_control_client.message_callback_add(v_thing_topic + "/" + control_in_suffix,
                                                 self.on_message_in_control_vThing)
        mqtt_control_client.message_callback_add(tv_control_prefix + "/" + thing_visor_ID + "/" + control_in_suffix,
                                                 self.on_message_in_control_TV)
        mqtt_control_client.subscribe(v_thing_topic + '/' + control_in_suffix)
        mqtt_control_client.subscribe(tv_control_prefix + "/" + thing_visor_ID + "/" + control_in_suffix)
        mqtt_control_client.loop_forever()
        print("Thread '" + self.name + "' terminated")


# main
if __name__ == '__main__':
    resources_ip = "127.0.0.1"
    camera_end_point = ""
    ca_server = ""

    # Only for test
    '''
    os.environ = {'MQTTDataBrokerIP': resources_ip,
                    'MQTTDataBrokerPort': 1883,
                    'MQTTControlBrokerIP': resources_ip,
                    'MQTTControlBrokerPort': 1883,
                    'params': {},
                    'thingVisorID': 'ribbon-tv',
                    'systemDatabaseIP': "172.17.0.2",
                    'systemDatabasePort': 27017}
    '''

    thing_visor_ID = os.environ["thingVisorID"]
    parameters = os.environ["params"]
    if parameters:
        try:
            params = json.loads(parameters.replace("'", '"'))
        except json.decoder.JSONDecodeError:
            # TODO manage exception
            print("error on params (JSON) decoding")
            os._exit(1)
        except KeyError:
            print(Exception.with_traceback())
            os._exit(1)
        except Exception as err:
            print("ERROR on params (JSON)", err)

    if 'vThingName' in params.keys():
        v_thing_name = params['vThingName']
    else:
        v_thing_name = "vThingCBPF"
    if 'vThingType' in params.keys():
        v_thing_type_attr = params['vThingType']
    else:
        v_thing_type_attr = "message"

    if 'cameraEndpoint' in params.keys():
        camera_end_point = params['cameraEndpoint']
    else:
        print ("error no camera end point")
        os._exit(1)
    
    if 'caServer' in params.keys():
        ca_server = params['caServer']
    else:
        print ("error no ca server")
        os._exit(1)

    if 'requestRate' in params.keys():
        request_rate = int(params['requestRate'])
    else:
        request_rate = 5

    v_thing_label = v_thing_name
    v_thing_description = "CBPF ThingVisor for camera virtualization system"
    v_thing_ID = thing_visor_ID + "/" + v_thing_name

    if "/" in v_thing_ID:
        _v_thing_id = v_thing_ID.replace("/", ":")
    else:
        _v_thing_id = v_thing_ID

    v_thing_ID_LD = "urn:ngsi-ld:"+ _v_thing_id

    v_thing = {"label": v_thing_label,
               "id": v_thing_ID,
               "description": v_thing_description}

    '''
    # Mongodb settings
    time.sleep(1.5)
    db_name = "viriotDB"
    thing_visor_collection = "thingVisorC"
    db_IP = os.environ['systemDatabaseIP']
    db_port = os.environ['systemDatabasePort']
    db_client = MongoClient('mongodb://' + db_IP + ':' + str(db_port) + '/')
    db = db_client[db_name]
    tv_entry = db[thing_visor_collection].find_one({"thingVisorID": thing_visor_ID})
    MAX_RETRY = 3

    valid_tv_entry = False
    for x in range(MAX_RETRY):
        if tv_entry is not None:
            value_tv_entry = True
            break
        time.sleep(3)
    if not valid_tv_entry:
        print ("Error: ThingVisor entry not found for thing_visor_ID: ", thing_visor_ID)
        exit()
    '''

    MQTT_data_broker_IP = os.environ["MQTTDataBrokerIP"]
    MQTT_data_broker_port = int(os.environ["MQTTDataBrokerPort"])
    MQTT_control_broker_IP = os.environ["MQTTControlBrokerIP"]
    MQTT_control_broker_port = int(os.environ["MQTTControlBrokerPort"])

    # sub_rn = v_thing_ID.replace("/",":") + "_subF4I"
    # vtype = ""

    # Context is a "map" of current virtual thing state
    commands = ["start", "close"]
    context_vThing = Context()

    # mapping of virtual thing with its context object. Useful in case of multiple virtual things
    contexts = {v_thing_ID: context_vThing}

    # Mqtt settings
    tv_control_prefix = "TV"  # prefix name for controller communication topic
    v_thing_prefix = "vThing"  # prefix name for virtual Thing data and control topics
    data_out_suffix = "data_out"
    data_in_suffix = "data_in"
    control_in_suffix = "c_in"
    control_out_suffix = "c_out"
    v_silo_prefix = "vSilo"

    '''
    # Mongodb settings
    time.sleep(1.5)  # wait before query the system database
    db_name = "viriotDB"  # name of system database
    thing_visor_collection = "thingVisorC"
    db_IP = os.environ['systemDatabaseIP']  # IP address of system database
    db_port = os.environ['systemDatabasePort']  # port of system database
    db_client = MongoClient('mongodb://' + db_IP + ':' + str(db_port) + '/')
    db = db_client[db_name]
    port_mapping = db[thing_visor_collection].find_one({"thingVisorID": thing_visor_ID}, {"port": 1, "_id": 0})
    poa_IP_dict = db[thing_visor_collection].find_one({"thingVisorID": thing_visor_ID}, {"IP": 1, "_id": 0})
    poa_IP = str(poa_IP_dict['IP'])
    print("poa_IP->", poa_IP)
    poa_port = port_mapping['port'][str(flask_port)+'/tcp']
    if not poa_IP:
        poa_IP = socket.gethostbyname(socket.gethostname())
    if not poa_port:
        poa_port = flask_port
    notification_URI = ["http://" + poa_IP + ":" + poa_port + "/notify"]
    '''

    # set v_thing_topic the name of mqtt topic on witch publish vThing data
    # e.g vThing/helloWorld/hello
    v_thing_topic = v_thing_prefix + "/" + v_thing_ID

    # threadPoolExecutor of size one to handle one command at a time in a fifo order
    executor = ThreadPoolExecutor(1)

    mqtt_control_client = mqtt.Client()
    mqtt_data_client = mqtt.Client()

    #rxThread = httpRxThread()  # http server used to receive JSON messages from external producer
    #rxThread.start()

    mqtt_control_thread = mqttControlThread()       # mqtt VirIoT control thread
    mqtt_control_thread.start()

    mqtt_data_thread = mqttDataThread()       # mqtt VirIoT data thread
    mqtt_data_thread.start()

    #mqtt_ribbon_thread = mqttRxThread()             # mqtt data thread
    #mqtt_ribbon_thread.start()

    time.sleep(2)
    while True:
        try:
            time.sleep(3)
        except:
            print("KeyboardInterrupt")
            time.sleep(1)
            os._exit(1)
