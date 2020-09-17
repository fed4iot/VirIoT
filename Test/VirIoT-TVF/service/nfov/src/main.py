import sys, socket, json
from logging import basicConfig, getLogger, DEBUG

#add import files
import cv2, base64, os
from math import pi
import numpy as np
import imageio as im
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
        self.height = int(setting["height"])
        self.width = int(setting["width"])
        self.center_point = setting["center_point"]
        self.FOV = setting["fov"]
        self.PI = pi
        self.PI_2 = pi * 0.5
        self.PI2 = pi * 2.0
        
        if (self.logLevel == "debug"):
            basicConfig(level=DEBUG)
        self.logger = getLogger(__name__)

    def _get_coord_rad(self, isCenterPt, center_point=None):

        self.logger.debug("[_get_coord_rad]")
        return (center_point * 2 - 1) * np.array([self.PI, self.PI_2]) \
            if isCenterPt \
            else \
            (self.screen_points * 2 - 1) * np.array([self.PI, self.PI_2]) * (
                np.ones(self.screen_points.shape) * self.FOV)

    def _get_screen_img(self):

        self.logger.debug("[_get_screen_img]")
        xx, yy = np.meshgrid(np.linspace(0, 1, self.width), np.linspace(0, 1, self.height))
        return np.array([xx.ravel(), yy.ravel()]).T

    def _calcSphericaltoGnomonic(self, convertedScreenCoord):

        self.logger.debug("[_calcSphericaltoGnomonic]")
        x = convertedScreenCoord.T[0]
        y = convertedScreenCoord.T[1]

        rou = np.sqrt(x ** 2 + y ** 2)
        c = np.arctan(rou)
        sin_c = np.sin(c)
        cos_c = np.cos(c)

        lat = np.arcsin(cos_c * np.sin(self.cp[1]) + (y * sin_c * np.cos(self.cp[1])) / rou)
        lon = self.cp[0] + np.arctan2(x * sin_c, rou * np.cos(self.cp[1]) * cos_c - y * np.sin(self.cp[1]) * sin_c)

        lat = (lat / self.PI_2 + 1.) * 0.5
        lon = (lon / self.PI + 1.) * 0.5

        return np.array([lon, lat]).T

    def _bilinear_interpolation(self, screen_coord):

        self.logger.debug("[_bilinear_interpolation]")
        uf = np.mod(screen_coord.T[0],1) * self.frame_width  # long - width
        vf = np.mod(screen_coord.T[1],1) * self.frame_height  # lat - height

        x0 = np.floor(uf).astype(int)  # coord of pixel to bottom left
        y0 = np.floor(vf).astype(int)
        x2 = np.add(x0, np.ones(uf.shape).astype(int))  # coords of pixel to top right
        y2 = np.add(y0, np.ones(vf.shape).astype(int))

        base_y0 = np.multiply(y0, self.frame_width)
        base_y2 = np.multiply(y2, self.frame_width)

        A_idx = np.add(base_y0, x0)
        B_idx = np.add(base_y2, x0)
        C_idx = np.add(base_y0, x2)
        D_idx = np.add(base_y2, x2)

        flat_img = np.reshape(self.frame, [-1, self.frame_channel])

        A = np.take(flat_img, A_idx, axis=0)
        B = np.take(flat_img, B_idx, axis=0)
        C = np.take(flat_img, C_idx, axis=0)
        D = np.take(flat_img, D_idx, axis=0)

        wa = np.multiply(x2 - uf, y2 - vf)
        wb = np.multiply(x2 - uf, vf - y0)
        wc = np.multiply(uf - x0, y2 - vf)
        wd = np.multiply(uf - x0, vf - y0)

        # interpolate
        AA = np.multiply(A, np.array([wa, wa, wa]).T)
        BB = np.multiply(B, np.array([wb, wb, wb]).T)
        CC = np.multiply(C, np.array([wc, wc, wc]).T)
        DD = np.multiply(D, np.array([wd, wd, wd]).T)
        nfov = np.reshape(np.round(AA + BB + CC + DD).astype(np.uint8), [self.height, self.width, 3])

        return nfov

    def toNFOV(self, frame, center_point):

        self.logger.debug("[toNFOV]")
        self.frame = frame
        self.frame_height = frame.shape[0]
        self.frame_width = frame.shape[1]
        self.frame_channel = frame.shape[2]

        self.cp = self._get_coord_rad(center_point=center_point, isCenterPt=True)
        convertedScreenCoord = self._get_coord_rad(isCenterPt=False)
        spericalCoord = self._calcSphericaltoGnomonic(convertedScreenCoord)

        return self._bilinear_interpolation(spericalCoord)

    def encode(self):
        
        if self.codec == "jpg":
            encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), self.quality]
            result, encImg = cv2.imencode(".jpg", self.nfovFrame, encode_param)

        if self.codec == "png":
            encode_param = [int(cv2.IMWRITE_PNG_QUALITY), self.quality]
            result, encImg = cv2.imencode(".png", self.nfovFrame, encode_param)

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
        srcImg = cv2.imread("temp.jpg", 1)

        orgH, orgW, orgC = srcImg.shape

        self.logger.debug("source resolution: {} {}".format(orgH, orgW))

        #DATA = []

        center_point = self.center_point

        data = self.revData[self.targetService]
        if (self.targetService == "yolo" or self.targetService == "yologpu" or self.targetService == "yolotiny"):
            key = "boundingBox"
            for i in range(len(data)):
                if (data[i]['tagName'] == self.targetTag):
                    left = int(data[i][key]['left'])
                    right = int(data[i][key]['top'])
                    top = int(data[i][key]['width'])
                    bottom = int(data[i][key]['height'])

                    #normailized by [0:1]
                    center_point = np.array([round((left+right)/(2*orgW),1), round((top+bottom)/(2*orgH),1)])

        elif (self.targetService == "face"):
            key = "faceRectangle"
            for i in range(len(data)):
                left = int(data[i][key]['left'])
                top = int(data[i][key]['top'])
                width = int(data[i][key]['width'])
                height = int(data[i][key]['height'])
                right = left + width
                bottom = top + hight

                #normailized by [0:1]
                center_point = np.array([round((left+right)/(2*orgW),1), round((top+bottom)/(2*orgH),1)])

        self.logger.debug("center point {}".format(center_point))

        self.screen_points = self._get_screen_img()

        self.logger.debug("screen point {}".format(self.screen_points))

        self.nfovFrame = self.toNFOV(srcImg, center_point)
        encImg = self.encode()
        
        byteImg = base64.b64encode(encImg).decode('utf-8')

        self.logger.debug("transform complete")

        DATA = byteImg
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
