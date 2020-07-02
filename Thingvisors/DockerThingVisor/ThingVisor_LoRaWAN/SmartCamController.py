import logging

from helpers.chirpstack import AppController, DeviceController


log_handler = logging.StreamHandler()
log_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
log_handler.setFormatter(log_formatter)
root_logger = logging.getLogger()
root_logger.addHandler(log_handler)
root_logger.setLevel(logging.DEBUG)

log = logging.getLogger(__name__)


class SmartCamController(DeviceController):
    """
    Class to control the smartcam through high level API
    """
    def __init__(self, deveui, app):
        DeviceController.__init__(self, deveui, app)
        self.switch = {True:1,False:0}
        
    def switch_func_person_count(self, on=True):
        sw = self.switch[on]
        self.downlink(f"PC:{sw}")

    def switch_func_car_count(self, on=True):
        sw = self.switch[on]
        self.downlink(f"CC:{sw}")

    def on_uplink_decoded(self, msg):
        #TODO input data management - call appropriate event (person_count, car_count)
        log.debug(f"uplink_decoded received in smartcam controller:{msg.payload}")
        
    def event_person_count(self):
        None

    def event_car_count(self):
        None


        
