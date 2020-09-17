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

FLAG = "./flag"
TEMP = "./temp.jpg"

class MyHandler(FTPHandler):

    #def __init__(self):

    #read config file
    with open('config.json', "r") as fp:
        setting = json.load(fp)

    host = setting["host"]
    port = setting["port"]
    segSize = setting["segSize"]

    location = setting["location"]
    devType = setting["devType"]
    point = setting["point"]
    interest = setting["interest"]

    def on_connect(self):
        print("{}:{} connected".format(str(self.remote_ip), str(self.remote_port))) 

    def on_disconnect(self):
        print("{}:{} disconnected".format(str(self.remote_ip). str(self.remote_port)))

    def on_file_received(self, file):

        if (os.path.exists(FLAG) == True):
            os.remove(FLAG)
        self.revFileName = file
        print("{} received".format(str(self.revFileName)))
        os.rename(self.revFileName, TEMP)

        temp = pathlib.Path(FLAG)
        temp.touch()


def runFtpServer():

    #read config file
    with open('config.json', "r") as fp:
        setting = json.load(fp)

    ftpHost = setting["ftpHost"]
    ftpPort = setting["ftpPort"]
    ftpUser = setting["ftpUser"]
    ftpPasswd = setting["ftpPasswd"]
    ftpHome = setting["ftpHome"]

    #Run ftp server
    authorizer = DummyAuthorizer()
    authorizer.add_user(ftpUser, ftpPasswd, homedir=ftpHome, perm='elradfmw')

    handler = MyHandler
    handler.authorizer = authorizer
    server = FTPServer((ftpHost, ftpPort), handler)
    server.serve_forever()

def reset():

     if (os.path.exists(FLAG) == True):
            os.remove(FLAG)
            print ("remove flag")

     if (os.path.exists(TEMP) == True):
            os.remove(TEMP)
            print ("remove image")
    
if __name__ == '__main__':

    reset()
    runFtpServer()
