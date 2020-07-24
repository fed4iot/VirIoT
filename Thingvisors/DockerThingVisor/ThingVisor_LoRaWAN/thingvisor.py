VERSION = "0.1.0"

import logging
import json

log_handler = logging.StreamHandler()
log_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
log_handler.setFormatter(log_formatter)
root_logger = logging.getLogger()
root_logger.addHandler(log_handler)
root_logger.setLevel(logging.DEBUG)

log = logging.getLogger(__name__)
log.info(f"LoRaWAN ThingVisor - {VERSION}")

# ####

import os, json, time
from base64 import b64decode

from viriot import VThing, ThingVisor
from ThermometerController import ThermometerController
from SmartCamController import SmartCamController
from helpers.mqtt import MqttBroker
from helpers.chirpstack import AppController
from helpers.data_model import SmartCamera, CameraEventDetector, Site, Thermometer

def do_nothing():
    """ A small helper function that does nothing """
    None


class VThing_Thermometer(VThing, ThermometerController):
    def __init__(self, id, label, deveui, csapp, params):
        log.debug(f"Creating thermometer vThing:{id}:{label}:{deveui}")
        VThing.__init__(self, id, label, label)
        ThermometerController.__init__(self,deveui,csapp)
        self.thermometer = Thermometer(f"{deveui}")
        self.context.register(self.thermometer)

        site_params = params.get("site")
        self.site = Site(site_params["id"])
        self.thermometer.set_site(self.site)
        self.context.register(self.site)
        
    def on_uplink_decoded(self, msg):
        log.debug(f"THERMOMETER UPLINK : {msg.topic} : {msg.payload}")
        data = json.loads(msg.payload)
        temperature = next((prop['v'] for prop in data if prop['n']=='temperature'), None)
        humidity =  next((prop['v'] for prop in data if prop['n']=='humidity'), None)
        self.site.temperature = temperature
        self.site.humidity = humidity
        log.info(f"THERMOMETER {self.id} update T:{temperature} H:{humidity}")
        self.publish_context()
    
class VThing_SmartCam(VThing, SmartCamController):
    def __init__(self, id, label, deveui, csapp, params):
        VThing.__init__(self, id, label, label)
        SmartCamController.__init__(self, deveui, csapp)

        self.data_model_camera = SmartCamera(f"{deveui}")
        self.context.register(self.data_model_camera)

        self.data_model_detector_entry = CameraEventDetector(f"{self.id}_entryDetector", self.data_model_camera)
        self.data_model_detector_exit = CameraEventDetector(f"{self.id}_exitDetector", self.data_model_camera)
        self.context.register(self.data_model_detector_entry)
        self.context.register(self.data_model_detector_exit)

        site_params = params.get("site")
        if (site_params):
            self.data_model_site = Site(site_params["id"])
            self.data_model.camera.set_site(self.data_model_site)
            self.context.register(self.data_model_site)
            # TODO : more Site parameters

    def event_person_count(self):
        None

    def event_car_count(self):
        None
    

device_manager_builder = {
    'smartcam' : VThing_SmartCam,
    'thermometer' : VThing_Thermometer
}


def after_connect():

    log.debug("ThingVisor connected to MQTT brokers. Now configuring devices.")
    # Connecting to the requested devices
    devices = params["devices"]
    csapp_list = {}
    v_things = []
    for device in devices :
        devtype = device["type"]
        label = device["label"]
        appid = device["appid"]
        device_params = device.get("params")
        csapp = csapp_list.get(appid)
        if(csapp is None):
            log.debug(f"Creating new app controller:{appid}")
            csapp = AppController(appid, csbroker)
            csapp_list[appid] = csapp
        
        deveui = device["deveui"]
        devid = f"{thing_visor_ID}/{appid}/{deveui}"

        log.info(f"Configuring connection to device:{devid} type:{devtype}")
        
        vthing_creator = device_manager_builder.get(devtype)
        if (vthing_creator) :
            vthing = vthing_creator(devid, label, deveui, csapp, device_params)
            thingvisor.register(vthing)
            v_things.append(vthing)
        else :
            log.error(f"Unknown device type:{devtype} / {device_manager_builder}")


def create_file_with_content(fname,content):
    if (content) :
        print(f"creating file {fname}")
        with open(fname,"wb") as fh:
            fh.write(b64decode(content))
        

if __name__ == '__main__':

    log.info("-- Starting Smartcam ThingVisor --")
    log.info(f"VERSION {VERSION}")
    log.debug(f"Environment : {os.environ}")
    
    # Viriot pub/sub system
    MQTT_data_broker_IP = os.environ["MQTTDataBrokerIP"]
    MQTT_data_broker_port = int(os.environ["MQTTDataBrokerPort"])
    MQTT_control_broker_IP = os.environ["MQTTControlBrokerIP"]
    MQTT_control_broker_port = int(os.environ["MQTTControlBrokerPort"])

    # Getting thingvisor parameters
    thing_visor_ID = os.environ["thingVisorID"]
    thingvisor = ThingVisor(MQTT_control_broker_IP, MQTT_control_broker_port, thing_visor_ID)
    #TODO : maybe take into account distinct brokers for data and control as permitted by viriot
    thingvisor.start()
    
    params = os.environ["params"]
    params = json.loads(params.replace("'", '"'))

    # Smart cams broker
    chirpstack_mqtt_server =  params["chirpstack_mqtt_server"]
    chirpstack_mqtt_port =  int(params["chirpstack_mqtt_port"])

    chirpstack_cafile =  params.get("chirpstack_cafile")
    create_file_with_content("ca.crt", chirpstack_cafile)
    
    chirpstack_crtfile =  params.get("chirpstack_crtfile")
    create_file_with_content("user.crt", chirpstack_crtfile)
    
    chirpstack_keyfile =  params.get("chirpstack_keyfile")
    create_file_with_content("user.key", chirpstack_keyfile)
    
    csbroker = MqttBroker(chirpstack_mqtt_server, chirpstack_mqtt_port, do_nothing)
    if (chirpstack_cafile) : csbroker.ca_file = "ca.crt"
    if (chirpstack_crtfile) : csbroker.crt_file = "user.crt"
    if (chirpstack_keyfile) : csbroker.key_file = "user.key"
    
    csbroker.start()

    log.debug("Waiting for mqtt brokers to be connected")
    while(not(csbroker.connected and thingvisor.connected)):
        time.sleep(1)

    after_connect()
    
    #TODO: Maybe insert here a monitoring loop
    
    csbroker.join()
    thingvisor.join()
    

        
    
