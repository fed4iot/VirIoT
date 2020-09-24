import sys, socket, json

import cv2
import base64

class SF():

    def __init__(self):

        #read confi file
        with open('config.json', "r") as fp:
            setting = json.load(fp)

        self.host = setting["host"]
        self.port = setting["port"]
        self.segSize = setting["segSize"]
        self.devID = setting["devID"]
        self.codec = setting["codec"]
        self.quality = setting["quality"]
        self.width = setting["width"]
        self.height = setting["height"]
        self.location = setting["location"]
        self.devType = setting["devType"]
        self.point = setting["point"]
        self.interest = setting["interest"]

    #define service function
    def callServiceFunction(self):

        print ("[callServiceFunction] open camera device")
        cam = cv2.VideoCapture(int(self.devID))
        cam.set(3, self.width)
        cam.set(4, self.height)
        print ("[callServiceFunction] camera is ready")

        print ("[callServiceFunction] capture one frame")
        ret, frame = cam.read()

        if self.codec == "jpg":
            encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), self.quality]
            result, encImg = cv2.imencode(".jpg", frame, encode_param)

        if self.codec == "png":
            encode_param = [int(cv2.IMWRITE_PNG_QUALITY), self.quality]
            result, encImg = cv2.imencode(".png", frame, encode_param)

        print ("[callServiceFunction] jpeg encode complete")

        binImg = base64.b64encode(encImg).decode('utf-8')

        print ("[callServiceFunction] base64 encode complete")

        TEMP = {"id": self.location + ":" + self.interest, "type": self.devType,
                "content": {"type": "Property", "value": binImg},
            "geometry": {"type": "Point", "coordinates": self.point}}

        BODY = {self.interest: TEMP}
        BODY = json.dumps(BODY)

        print ("[callServiceFunction] capture complete")

        return BODY.encode()

    def run(self):

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:

            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind((self.host, self.port))
            s.listen(10)

            while True:

                print ("[callServiceFunction] waiting")
                clientsock, client_address = s.accept()

                try:
                    print ("[callServiceFunction] accepted")

                    #all_data = b''

                    #while True:

                    #    data = clientsock.recv(SEGSIZE)

                    #    if not data:
                    #        break
                    #    all_data += data

                    #print ("[callServiceFunction] received")

                    print ("[callServiceFunction] callServiceFunction")
                
                    result = self.callServiceFunction()

                    print ("[callServiceFunction] send results")
                    clientsock.send(result)

                    print ("[callServiceFunction] send complete")

                except Exception as e:
                    print ("[callServiceFunction] error")
                    print (e)

                finally:
                    clientsock.close()


if __name__ == '__main__':

    sf = SF()
    sf.run()
