import sys, socket, json
from logging import basicConfig, getLogger, DEBUG

#add import files
import cv2, base64, os
######

class SF():

    def __init__(self):

        #read config file
        with open('config.json', "r") as fp:
            setting = json.load(fp)

        self.host = setting["host"]
        self.port = setting["port"]
        self.segSize = setting["segSize"]
        self.serviceType = setting["service type"]
        self.serviceName = setting["service name"]
        self.logLevel = setting["logLevel"]
        self.targetService = setting["target service"]
        self.targetTag = setting["target tag"]
        self.content = setting["content name"]
        self.codec = setting["codec"]
        self.quality = setting["quality"]
        self.ratio = setting["ratio"]

        if (self.logLevel == "debug"):
            basicConfig(level=DEBUG)
        self.logger = getLogger(__name__)

    def mosaic_area(self):

        result = self.srcImg.copy()
        method = cv2.INTER_NEAREST
        result[self.top:self.bottom, self.left:self.right] = cv2.resize(cv2.resize(result[self.top:self.bottom,self.left:self.right], None, fx=self.ratio, fy=self.ratio, interpolation=method), result[self.top:self.bottom,self.left:self.right].shape[:2][::-1], interpolation=method)

        return result

    def encode(self):
        
        if self.codec == "jpg":
            encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), self.quality]
            result, encImg = cv2.imencode(".jpg", self.mosaicImg, encode_param)

        if self.codec == "png":
            encode_param = [int(cv2.IMWRITE_PNG_QUALITY), self.quality]
            result, encImg = cv2.imencode(".png", self.mosaicImg, encode_param)

        return encImg

    #define service function
    def callServiceFunction(self):

        self.logger.debug("[callServiceFunction] start service function")
        self.revData = self.revData.decode()
        self.revData = json.loads(self.revData)

        temp = self.revData[self.content]['content']['value']
        byteImg = base64.b64decode(temp.encode('utf-8'))

        with open("temp.jpg", "wb") as f:
            f.write(byteImg)
        self.srcImg = cv2.imread("temp.jpg", 1)

        #DATA = []

        data = self.revData[self.targetService]
        if (self.targetService == "yolo" or self.targetService == "yologpu" or self.targetService == "yolotiny"):
            key = "boundingBox"
            for i in range(len(data)):
                if (data[i]['tagName'] == self.targetTag):
                    self.left = int(data[i][key]['left'])
                    self.right = int(data[i][key]['top'])
                    self.top = int(data[i][key]['width'])
                    self.bottom = int(data[i][key]['height'])

                    #crop
                    self.mosaicImg = self.mosaic_area()
            
        elif (self.targetService == "face"):
            key = "faceRectangle"
            for i in range(len(data)):
                self.left = int(data[i][key]['left'])
                self.top = int(data[i][key]['top'])
                width = int(data[i][key]['width'])
                height = int(data[i][key]['height'])

                self.right = self.left + width
                self.bottom = self.top + height

                #crop
                self.mosaicImg = self.mosaic_area()

        encImg = self.encode()
        DATA = base64.b64encode(encImg).decode('utf-8')
        self.revData[self.content]['content']['value'] = DATA

        metadata = {"service info": {"name": self.serviceName, "type": self.serviceType, 
                    "target": {"service": self.targetService, "tag": self.targetTag}
                    }}

        self.revData.update(metadata)

        BODY = json.dumps(self.revData)
        #self.logger.debug("[callServiceFunction] result{}".format(BODY))
        ##########

        self.logger.debug("[callServiceFunction] complete")
        os.remove("temp.jpg")

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

                    self.revData = b''

                    while True:

                        data = clientsock.recv(self.segSize)

                        if not data:
                            break
                        self.revData += data
                    
                    self.logger.debug("[callServiceFunction] received")

                    self.logger.debug("[callServiceFunction] callServiceFunction")
            
                    result = self.callServiceFunction()

                    self.logger.debug("[callServiceFunction] send results")
                    clientsock.sendall(result)

                    self.logger.debug("[callServiceFunction] send complete")

                except Exception as e:
                    self.logger.debug("[callServiceFunction] error")
                    self.logger.debug(e)

                finally:
                    clientsock.close()

if __name__ == '__main__':

    sf = SF()
    sf.run()
