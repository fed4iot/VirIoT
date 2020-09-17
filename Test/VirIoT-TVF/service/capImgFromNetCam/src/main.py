import sys, socket, json

#add import files
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer
from pyftpdlib.authorizers import DummyAuthorizer
import os
import base64
import sys
import threading
import pathlib
######

class SF():

    def __init__(self):

        #read config file
        with open('config.json', "r") as fp:
            setting = json.load(fp)

        self.host = setting["host"]
        self.port = setting["port"]
        self.segSize = setting["segSize"]

        self.location = setting["location"]
        self.devType = setting["devType"]
        self.point = setting["point"]
        self.interest = setting["interest"]

    #define service function
    def callServiceFunction(self):

        print ("[callServiceFunction] start service function")

        #please write your own function
        ##self.revData: receved data from network function

        while True:

            if (os.path.exists("./flag") == True):
                with open("./temp.jpg", 'rb') as f:
                    img = f.read()
                break

        binImg = base64.b64encode(img).decode('utf-8')
        data = {"id": self.location + ":" + self.devType, "type": self.devType, 
                "content": {"type": "Property", "value": binImg},
                "geometry": {"type": "Point", "coordinates": self.point}}

        BODY = json.dumps({self.interest: data})
        ##########

        print ("[callServiceFunction] complete")

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

                    #self.revData = b''

                    #while True:

                    #    data = clientsock.recv(self.segSize)

                    #    if not data:
                    #        break
                    #    self.revData += data

                    print ("[callServiceFunction] received")

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

    #Run SF server
    sf = SF()
    #Run sf server
    sf.run()

