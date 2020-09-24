from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer
from pyftpdlib.authorizers import DummyAuthorizer
import os
import threading
import kafka
import json
import base64
import sys
import cefpyco
from datetime import datetime
from logging import basicConfig, getLogger, DEBUG, INFO

from common import common
from protocol import icnCefore

SETTING = "./config/nodeSetting.json"
FTP = "./config/ftpServer.json"

class MyHandler(FTPHandler):

    funcList = common.analyzeInterest(str(sys.argv[1]))
    print ("[main] input interest name: {}".format(funcList))

    with open(SETTING, "r") as fp:
        setting = common.jsonReader(fp)

    with open(FTP, "r") as fp:
        ftpsetting = common.jsonReader(fp)

    SLEEP = int(setting["sleep"])/1000 #(sec)
    CACHETIME = int(setting["cache time"]) #(msec)
    EXPIRY = int(setting["expiry"]) #(msec)
    TIMEOUT = int(setting["timeout"]) #(msec)
    segSize = int(setting["segSize"])
    MODE = setting["mode"]
    icnMODE = setting["icnMode"]
    BROKER = setting["broker"]
    location = ftpsetting["location"]
    sensor = ftpsetting["devType"]
    geometry = ftpsetting["geometry"]
    logLevel = ftpsetting["logLevel"]
    revFileName = "null"

    if (logLevel == "info"):
        basicConfig(level=INFO)
    if (logLevel == "debug"):
        basicConfig(level=DEBUG)
    logger = getLogger(__name__)

    if (funcList[0] == "kafka:"):
        logger.debug("[pubPanaCam] connect to kafka broker")
        producer = kafka.KafkaProducer(bootstrap_servers=BROKER)

    icnSetting = {"segSize":segSize, "cacheTime":CACHETIME, "expiry": EXPIRY, "timeout":TIMEOUT}

    def on_connect(self):
        self.logger.info("{}:{} connceted".format(str(self.remote_ip), str(self.remote_port)))

    def on_disconnect(self):
        self.logger.info("{}:{} disconnected".format(str(self.remote_ip), str(self.remote_port)))

    def on_file_received(self, file):
        
        self.revFileName = file
        
        self.logger.info("{} received".format(str(self.revFileName)))
        
        if (self.funcList[0] == "ccn:"):
            self.logger.info("[pubPanaCam] mode ccn")
            thread = threading.Thread(target=self.icnPublish())
        if (self.funcList[0] == "kafka:"):
            self.logger.info("[pubPanaCam] mode kafka")
            thread = threading.Thread(target=self.kafkaPublish())
        thread.start()
        
        os.remove(file)
        self.logger.info("{} removed".format(str(file)))


    def icnPublish(self):

        with cefpyco.create_handle() as handle:
        
            with open(self.revFileName, 'rb') as f:
                img = f.read()
                binImg = base64.b64encode(img).decode('utf-8')

                ts = datetime.now()

                ngsiLdEntity = {"id": self.location + ":" + self.funcList[1],
                            "type": self.sensor,
                            "timestamp": {"type": "date time", "value": str(ts)},
                            "content": {"type": "Property", "value": binImg},
                            "geometry": self.geometry}

                #print (ngsiLdEntity)

                message = json.dumps({self.funcList[1]: ngsiLdEntity})
                #message = message.encode('utf-8')

                #reqName = (self.funcList[0], self.MODE, self.funcList[1])
                reqName = (self.funcList[0], self.funcList[1])
                icnCefore.asyncIcnPubContentV3(handle, message, reqName, self.icnSetting)
                #icnCefore.asyncIcnPubContent(handle, message, reqName, self.icnSetting)
                #icnCefore.syncIcnPubContent(handle, message, reqName, self.icnSetting)

                self.logger.info("[main] publish complete!")

    def kafkaPublish(self):
        
        with open(self.revFileName, 'rb') as f:
            img = f.read()
        
        binImg = base64.b64encode(img).decode('utf-8') 

        ts = datetime.now()
            
        ngsiLdEntity = {"id": self.location + ":" + self.funcList[1], "type": self.sensor, 
                "timestamp": {"type": "date time", "value": str(ts)},
                "content": {"type": "Property", "value": binImg}, 
                "geometry": self.geometry}
        
        message = json.dumps({self.funcList[1] : ngsiLdEntity})
        message = message.encode('utf-8')
        
        kafkaTopic = self.funcList[1]
        self.producer.send(kafkaTopic, message)
        
        self.logger.info("[kafkaPub] publish complete!")
        

def main():

    common.checkARG(len(sys.argv))
    
    with open(FTP, "r") as fp:
        setting = common.jsonReader(fp)

    HOST = setting["host"]
    PORT = int(setting["port"])
    USER = setting["user"]
    PASS = setting["passwd"]
    HOME = setting["homedir"]

    authorizer = DummyAuthorizer()
    authorizer.add_user(USER, PASS, homedir=HOME, perm='elradfmw')
	
    handler = MyHandler
    handler.authorizer = authorizer
    server = FTPServer((HOST,PORT), handler)
    server.serve_forever()

if __name__ == "__main__":
	main()
