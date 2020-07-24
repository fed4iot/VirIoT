import logging
import ssl
import traceback
from base64 import b64encode
from threading import Thread
import json

import paho.mqtt.client as mqtt


log = logging.getLogger(__name__)


class MqttBroker(Thread):
    """
    Thread to connect to a MQTT broker w/ a simplified interface.
    When connected calls the app callback given to __init__.
    ca_file, crt_file and key_file may be set to provide auth keys.
    The connection is made when the thread is started.

    Maybe already deprecated (was implemented for Chirpstack module) ?
    Main feature still used : subscribe(topic,callback)
    """
    
    def __init__(self, host, port, app):
        """
        Minimal initializations.
        Parameters:
        - host : the mqtt broker host
        - port : the mqtt broker port
        - app  : your callback to be called when connected
        """

        Thread.__init__(self)
        self.keepalive = 60 # ping interval default to 60 sec
        self.host = host
        self.port = port
        self.ca_file = None
        self.crt_file = None
        self.key_file = None
        self.cbmap = {}
        self.app = app
        self.connected = False

    def on_connect(self, client, userdata, flags, rc):
        """
        Notified when MQTT is connected.
        Launch the app startup code
        """
        log.info("connect event received")
        if rc != 0:
            log.fatal("Failed to connect to MQTT broker")
            exit(-1)
        log.info("Successfully connected to MQTT")
        try:
            self.connected = True
            self.app(self)
        except:
            treaceback.print_exception()
            log.fatal("Unexpected exception in app")

    def on_message(self, client, userdata, message):
        """
        Receive MQTT messages and dispatch
        """
        log.info(f"RX:{message.topic}:{message.payload}")
        cb = self.cbmap.get(message.topic,None)
        if cb:
            try:
                log.debug(cb)
                cb(message)
            except:
                log.error("Unexpected exception from topic callback")
                log.error(traceback.format_exc())
                
        else :
            log.error("How is this possible ? Callback should not be None.")

    def publish(self, topic, payload):
        """
        Publish a message on a given topic.
        """
        log.info(f"TX:{topic} <- {payload}")
        self.client.publish(topic, payload)

    def subscribe(self, topic, callback):
        """
        Subscribe a callback to a topic
        """
        if (callback is None) :
            return
        log.info(f"SUBSCRIBING:{topic}")
        self.cbmap[topic] = callback
        self.client.subscribe(topic)
        
    def run(self) :
        """
        Thread main code.
        """
        log.info(f"Starting thread for MQTT broker on {self.host}:{self.port}")
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        if self.ca_file :
            log.debug("using cert files")
            self.client.tls_set(
                ca_certs=self.ca_file,
                certfile=self.crt_file,
                keyfile=self.key_file,
                cert_reqs=ssl.CERT_REQUIRED,
                tls_version=ssl.PROTOCOL_TLS,
                ciphers=None
            )            
        
        try:
            self.client.connect(self.host, self.port, self.keepalive)
            log.info(f"MQTT loop start")
            self.client.loop_forever()
        except:
            log.error(f"Unexpected exception in MQTT thread for host:{self.host} - restarting loop")
            log.error(traceback.format_exc())
            

        
