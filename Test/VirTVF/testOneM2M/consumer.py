import requests
import json
import base64
import time
import sys
import ast
import os
import shutil

### OneM2M Broker ###
BROKER = "133.9.250.223"
PORT = "8000"
baseURI = "http://" + BROKER + ":" + PORT +"/onem2m/"
API = "latest"
###

RN = ["waseda", "netcam"]

SLEEP = 2

def getData():

    AE = RN[0]
    CNT = RN[1]

    end_point= baseURI + AE + "/" + CNT + "/" + API

    response = requests.get(end_point)

    result = response.json()
    data = result['m2m:cin']['con']

    # str -> dict
    data = ast.literal_eval(data)

    #Extract data
    ngsiID = data['id']
    ngsiType = data['type']
    ts = data['timestamp']
    byteImg = base64.b64decode(data['content']['value'].encode('utf-8'))
    geo = data['geometry']

    print (ngsiID)
    print (ngsiType)
    print (ts)
    print (geo)

    ####Save img to file
    #fname = "test.jpg"
    #imgFile = open(fname, 'wb')
    #imgFile.write(byteImg)

    ####Move file to html deirectoy####
    #if os.path.exists(DIR+"test.jpg") == True:
    #    os.remove(DIR+"test.jpg")
    #shutil.move('./test.jpg', DIR)
    #####

if __name__ == '__main__':

    while True:
        getData()
        time.sleep(SLEEP)

