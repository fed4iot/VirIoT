import sys, socket, json
from logging import basicConfig, getLogger, DEBUG

#add import files
import gphoto2 as gp
import os
import base64
######

class SF():

    def __init__(self):

        #read config file
        with open('config.json', "r") as fp:
            setting = json.load(fp)

        self.host = setting["host"]
        self.port = setting["port"]
        self.segSize = setting["segSize"]
        self.logLevel = setting["logLevel"]
        self.location = setting["location"]
        self.devType = setting["devType"]
        self.point = setting["point"]
        self.interest = setting["interest"]

        if (self.logLevel == "debug"):
            basicConfig(level=DEBUG)
        self.logger = getLogger(__name__)

    #define service function
    def callServiceFunction(self):

        self.logger.debug("[callServiceFunction] start service function")

        self.camera = gp.Camera()
        self.camera.init()

        #please write your own function
        ##self.revData: receved data from network function

        self.logger.debug("[callServiceFunction] capture image")
        filePath = self.camera.capture(gp.GP_CAPTURE_IMAGE)
        tarPath = os.path.join('.', filePath.name)
        
        self.logger.debug("[callServiceFunction] Copy image to {}".format(tarPath))
        cameraFile = self.camera.file_get(filePath.folder, filePath.name, gp.GP_FILE_TYPE_NORMAL)
        cameraFile.save(tarPath)

        self.camera.exit()

        #read image file
        with open(tarPath, 'rb') as f:
            img = f.read()

        os.remove(tarPath)

        binImg = base64.b64encode(img).decode('utf-8')

        ngsiLdEntity = {"id": self.location + ":" + self.interest, "type": self.devType,
                        "content": {"type": "Property", "value": binImg},
                        "geometry": {"type": "Point", "coordinates": self.point}}

        BODY = {self.interest: ngsiLdEntity}
        BODY = json.dumps(BODY)
        ##########

        self.logger.debug("[callServiceFunction] complete")

        return BODY.encode()

    def run(self):

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:

            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind((self.host, self.port))
            s.listen(10)

            while True:

                self.logger.debug("[callServiceFunction] waiting")
                clientsock, client_address = s.accept()

                try:
                    self.logger.debug("[callServiceFunction] accepted")

                    #self.revData = b''

                    #while True:

                    #    data = clientsock.recv(self.segSize)

                    #    if not data:
                    #        break
                    #    self.revData += data

                    #self.logger.debug("[callServiceFunction] received")

                    self.logger.debug("[callServiceFunction] callServiceFunction")
                
                    result = self.callServiceFunction()

                    self.logger.debug("[callServiceFunction] send results")
                    clientsock.send(result)

                    self.logger.debug("[callServiceFunction] send complete")

                except Exception as e:
                    self.logger.debug("[callServiceFunction] error")
                    self.logger.debug(e)

                finally:
                    clientsock.close()

if __name__ == '__main__':

    sf = SF()
    sf.run()
