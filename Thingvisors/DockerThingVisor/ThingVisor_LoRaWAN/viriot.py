import abc
import traceback
import json

from helpers.mqtt import MqttBroker
from helpers.data_model import Context

import logging
log = logging.getLogger(__name__)


class VThing(metaclass=abc.ABCMeta) :
    def __init__(self, id, label, description):
        self.id = id
        self.label = label
        self.description = description
        self.context = Context()


    @abc.abstractmethod
    def get_context(self):
        """ 
        Returns the NGSI-LD structure as a python dictionnary
        Abstract function : Must be implemented by subclasses
        """
        None

    def publish_data(self, data):
        self.thingvisor.publish(f"vThing/{self.id}/data_out", data)

    def publish_context(self):
        self.publish_data(self.get_context())    
    
    def init(self,thingvisor):
        self.thingvisor = thingvisor

        # Subscribe to control messages
        thingvisor.subscribe(f"vThing/{self.id}/c_in", self.on_control_message)

        # A new vThing is born, the world need to know
        message = {"command": "createVThing",
                   "thingVisorID": thingvisor.tvid,
                   "vThing":  {"label": self.label, "id": self.id, "description": self.description}}        
        self.thingvisor.publish(f"vThing/{self.id}/c_out",str(message).replace("\'", "\""))

    def destroy(self):
        msg = {"command": "deleteVThing", "vThingID": self.id, "vSiloID": "ALL"}
        self.thingvisor.publish(f"vThing/{self.id}/c_out", str(msg).replace("\'", "\""))

    def on_control_message(self, msg):
        log.debug("on_control_message")
        try:
            payload = msg.payload.decode("utf-8", "ignore")
            print(msg.topic + " " + str(payload))
            jres = json.loads(payload.replace("\'", "\""))
            command_type = jres["command"]
            if command_type == "getContextRequest":
                self.on_message_get_thing_context(jres)
        except:
            traceback.print_exc()
        return

    def on_message_get_thing_context(self, jres):
        log.debug("on_message_get_thing_context")
        try:
            silo_id = jres["vSiloID"]
            v_thing_id = jres["vThingID"]
            message = {"command": "getContextResponse", "data": self.get_context(), "meta": {"vThingID": self.id}}
            self.thingvisor.publish(f"vSilo/{silo_id}/c_in", str(message).replace("\'", "\""))
        except:
            log.error(traceback.format_exc())
            

        
class ThingVisor(MqttBroker):
    def __init__(self, host, port, tvid):
        """
        host, port : realted to MQTTControlBroker / MQTTDataBroker set to the same by default
                     TODO: manage distinct MQTT brokers as allowed by the viriot platform
        tvid : the thingvisor id
        """
        MqttBroker.__init__(self,host,port,self.runapp)
        self.data_broker = self
        self.tvid = tvid
        self.vthings = []

    def set_data_broker(self, host, port):
        # TODO if needed to have a distinct data broker
        None
        
    def register(self, vthing):
        vthing.init(self)
        
    def send_destroy_thing_visor_ack_message(self):
        msg = {"command": "destroyTVAck", "thingVisorID": self.tvid}
        mqtt_control_client.publish(f"TV/{self.tvid}/c_out",str(msg).replace("\'", "\""))
        return

    def on_message_destroy_thing_visor(self, jres):
        for vthing in self.vthings:
            vthing.destroy()
        self.send_destroy_thing_visor_ack_message()
        print("Shutdown completed")

    def on_message_in_control_TV(self, mosq, obj, msg):
        payload = msg.payload.decode("utf-8", "ignore")
        jres = json.loads(payload.replace("\'", "\""))
        try:
            command_type = jres["command"]
            if command_type == "destroyTV":
                self.on_message_destroy_thing_visor(jres)
        except Exception as ex:
            traceback.print_exc()
        return 'invalid command'

    def runapp(self):
        print("Smartcam controller started")
        self.subscribe(f"TV/{self.tvid}/c_in", self.on_message_in_control_TV)
