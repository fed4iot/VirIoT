from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer
from pyftpdlib.authorizers import DummyAuthorizer
import os
import threading
import requests
import json
import base64
import sys
import cefpyco
from datetime import datetime
from logging import basicConfig, getLogger, DEBUG, INFO

### OneM2M Broker ###
BROKER = ""
PORT = ""
headers = {'Content-Type':'application/vnd.onem2m-res+json',}
baseURI = 'http://'+BROKER+':'+PORT+'/onem2m/'
###

FTP = "ftpServer.json"

class MyHandler(FTPHandler):

    with open(FTP, "r") as fp:
        ftpsetting = json.load(fp)

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

    #OneM2M data format
    RN = [location, sensor]

    aeBody = { "m2m:ae":{
                    "rn": RN[0],
                    "api": "placeholder",
                    "rr": "TRUE"
                    }
            }
    
    cntBody = { "m2m:cnt": {
                    "rn": RN[1]
                    }
                }

    #Create oneM2M resource
    response = requests.post(baseURI, headers=headers, data=json.dumps(aeBody))
    logger.info("onem2m app resource create: {}".format(response))

    response = requests.post(baseURI+RN[0]+"/", headers=headers, data=json.dumps(cntBody))
    logger.info("onem2m container resource create: {}".format(response))
    #####


    def on_connect(self):
        self.logger.info("{}:{} connceted".format(str(self.remote_ip), str(self.remote_port)))

    def on_disconnect(self):
        self.logger.info("{}:{} disconnected".format(str(self.remote_ip), str(self.remote_port)))

    def on_file_received(self, file):
        
        self.revFileName = file
        
        self.logger.info("{} received".format(str(self.revFileName)))
        
        thread = threading.Thread(target=self.httpPublish())
        thread.start()
        
        os.remove(file)
        self.logger.info("{} removed".format(str(file)))

    def httpPublish(self):

        with open(self.revFileName, 'rb') as f:
            img = f.read()
        
        binImg = base64.b64encode(img).decode('utf-8') 

        ts = datetime.now()
            
        ngsiLdEntity = {"id": self.location + ":" + self.sensor, "type": self.sensor, 
                "timestamp": {"type": "date time", "value": str(ts)},
                "content": {"type": "Property", "value": binImg}, 
                "geometry": self.geometry}
        
        #OneM2M data format
        body = {"m2m:cin": {
                    "con": ngsiLdEntity,
                    "cnf": "text/plain:0"
                    }
                }
        endPoint = baseURI + self.RN[0] + "/" + self.RN[1] + "/"
        response = requests.post(endPoint, headers=headers, data=json.dumps(body))
        self.logger.info("[httpPublish] data publish to onem2m broker: {}".format(response))
        self.logger.info("[httpPublish] publish complete!")


def main():

    with open(FTP, "r") as fp:
        setting = json.load(fp)

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
