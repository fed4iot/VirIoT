import logging

from helpers.chirpstack import AppController, DeviceController

log = logging.getLogger(__name__)


class ThermometerController(DeviceController):
    """
    Class to control the smartcam through high level API
    """
    def __init__(self, deveui, app):
        DeviceController.__init__(self, deveui, app)
        self.switch = {True:1,False:0}
        
    def on_uplink_decoded(self, msg):
        #TODO input data management - call appropriate event (person_count, car_count)
        log.debug(f"uplink_decoded received in smartcam controller:{msg.payload}")
        

        
