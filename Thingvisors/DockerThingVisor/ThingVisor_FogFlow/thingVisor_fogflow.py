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

# Fed4IoT Thing ThingVisor hello world

import time
import os
import random
import json
import traceback
import paho.mqtt.client as mqtt
from threading import Thread

from fogflowclient import FogFlowClient, ContextEntity

# mqtt client for sending data
class mqttDataThread(Thread):
    def __init__(self, ip, port):
        Thread.__init__(self)
        
        self.MQTT_data_broker_IP = ip
        self.MQTT_data_broker_port = port               
        
        self.mqtt_data_client = mqtt.Client()

    # publish received data to data topic by using neutral format
    def publishData(self, v_thing_ID, data):
        v_thing_topic = "vThing/" + v_thing_ID

        message = {"data": data, "meta": {"vThingID": v_thing_ID}}
        print("topic name: " + v_thing_topic + '/data_out' + ", message: " + json.dumps(message))
        self.mqtt_data_client.publish(v_thing_topic + '/data_out',
                                 json.dumps(message)) 

    def run(self):
        print("Thread mqtt data started")
        self.mqtt_data_client.connect(self.MQTT_data_broker_IP, self.MQTT_data_broker_port, 30)
        self.mqtt_data_client.loop_forever()

# handler for mqtt control topics
class MqttControlThread(Thread):
    def __init__(self, ip, port):
        Thread.__init__(self)
                
        self.MQTT_control_broker_IP = ip
        self.MQTT_control_broker_port = port
        
        self.mqtt_control_client = mqtt.Client()      
        
        # prefix name for controller communication topic
        self.tv_control_prefix = "TV" 
        # prefix name for virtual Thing data and control topics
        self.v_thing_prefix = "vThing"  
        self.in_control_suffix = "c_in"
        out_control_suffix = "c_out"
        self.v_silo_prefix = "vSilo"          

    # -------- interfaces for virtual things ------------

    # create virtual things
    def createVThing(v_thing_ID, v_thing):
        global thing_visor_ID

        # Publish on the thingVisor out_control topic the createVThing command and other parameters
        v_thing_message = {"command": "createVThing",
                           "thingVisorID": thing_visor_ID,
                           "vThing": v_thing}

        self.mqtt_control_client.publish(self.tv_control_prefix + "/" + thing_visor_ID + "/" + out_control_suffix,
                                    json.dumps(v_thing_message))

        v_thing_topic = self.v_thing_prefix + "/" + v_thing_ID

        # Add message callbacks that will only trigger on a specific subscription match
        self.mqtt_control_client.message_callback_add(v_thing_topic + "/" + self.in_control_suffix,
                                                 self.on_message_in_control_vThing)
        self.mqtt_control_client.subscribe(v_thing_topic + '/' + in_control_suffix)

    # remove virtual things
    def send_destroy_v_thing_message(self):
        global v_things
        
        for v_thing in v_things:
            v_thing_ID = v_thing["vThing"]["id"]                
            msg = {"command": "deleteVThing", "vThingID": v_thing_ID, "vSiloID": "ALL"}
            self.mqtt_control_client.publish(self.v_thing_prefix + "/" + v_thing_ID + "/" + out_control_suffix, json.dumps(msg))

    def on_message_get_thing_context(self, jres):
        silo_id = jres["vSiloID"]
        v_thing_id = jres["vThingID"]
        
        global contexts
        
        message = {"command": "getContextResponse", "data": contexts[v_thing_id].get_all(), "meta": {"vThingID": v_thing_id}}
        self.mqtt_control_client.publish(self.v_silo_prefix + "/" + silo_id + "/" + self.in_control_suffix, json.dumps(message))

    def on_message_in_control_vThing(self, mosq, obj, msg):
        payload = msg.payload.decode("utf-8", "ignore")
        print(msg.topic + " " + str(payload))
        try:
            jres = json.loads(payload)
            command_type = jres["command"]
            if command_type == "getContextRequest":
                self.on_message_get_thing_context(jres)
        except Exception as ex:
            traceback.print_exc()

    # -------- interfaces for thing visor------------

    # stop this thing visor
    def on_message_destroy_thing_visor(self, jres):
        self.send_destroy_v_thing_message()
        self.send_destroy_thing_visor_ack_message()
        print("Shutdown completed")

    def send_destroy_thing_visor_ack_message(self):
        msg = {"command": "destroyTVAck", "thingVisorID": thing_visor_ID}
        self.mqtt_control_client.publish(self.tv_control_prefix + "/" + thing_visor_ID + "/" + out_control_suffix, json.dumps(msg))
        return
        
    # receive the intent from the updateThingVisor interface
    def on_message_update_thing_visor(self, jres):
        intent = jres['params']
        handleIntent(intent)          

    # handle the commands received from the control channel
    def on_message_in_control_TV(self, mosq, obj, msg):
        payload = msg.payload.decode("utf-8", "ignore")
        jres = json.loads(payload)

        print(msg.topic + " " + str(jres))

        try:
            command_type = jres["command"]
            if command_type == "destroyTV":
                self.on_message_destroy_thing_visor(jres)
            elif command_type == "updateTV":
                self.on_message_update_thing_visor(jres)
        except Exception as ex:
            traceback.print_exc()
        return 'invalid command'


    def run(self):
        print("Thread mqtt control started")
        self.mqtt_control_client.connect(self.MQTT_control_broker_IP, self.MQTT_control_broker_port, 30)

        global thing_visor_ID
        self.mqtt_control_client.message_callback_add("TV/" + thing_visor_ID + "/c_in",
                                                 self.on_message_in_control_TV)
        self.mqtt_control_client.subscribe("TV/" + thing_visor_ID + "/c_in")
        
        self.mqtt_control_client.loop_forever()


# handle the received notification from FogFlow
def onResult(ctxEntity):
    print(ctxEntity)
    

# handle the intent object sent by updateThingVisor
def handleIntent(intent):
    print(intent)

    global ffclient
    
    #trigger a service topology and then subscribe to the generated result
    sessionId = ffclient.start("test", onResult)       

# main
if __name__ == '__main__':
    # take the configuration from master controller
    thing_visor_ID = os.environ["thingVisorID"]            
        
    mqtt_control_thread = MqttControlThread(os.environ["MQTTControlBrokerIP"], int(os.environ["MQTTControlBrokerPort"]))  
    mqtt_control_thread.start()            
            
    mqtt_data_thread = mqttDataThread(os.environ["MQTTDataBrokerIP"], int(os.environ["MQTTDataBrokerPort"]))  
    mqtt_data_thread.start()

    # extract the URL of fogflow system
    jsonContent = os.environ["params"]
    if jsonContent:
        try:
            print(jsonContent)
            params = json.loads(jsonContent)
        except json.decoder.JSONDecodeError:
            print("error on params (JSON) decoding")
            os._exit(-1)  

    # initialize the connection to the FogFlow system                   
    FogFlowURL = params['FogFlowURL']    
    if FogFlowURL != None:
        print(FogFlowURL)
        ffclient = FogFlowClient(FogFlowURL)            
    
    # initialize the map of all virtual things managed by FogFlow ThingVisor
    contexts = {}
    
    while True:
        try:
            time.sleep(3)
        except:
            print("exit")
            os._exit(1)    
