import requests
import json
import base64
import time
import sys
import ast
import os
import shutil
import cv2

### OneM2M Broker ###
BROKER = ""
PORT = "8000"
baseURI = "http://" + BROKER + ":" + PORT +"/onem2m/"
API = "latest"
###

RN = ["waseda", "counter"]

SLEEP = 2

### HTML deirectory ###
DIR ="/var/www/html/app/"
outFileName = "test"
font = cv2.FONT_HERSHEY_COMPLEX_SMALL
font_size =1

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
    #ngsiID = data['id']
    #ngsiType = data['type']
    ts = data['timestamp']
    #byteImg = base64.b64decode(data['content']['value'].encode('utf-8'))
    geo = data['geometry']
    targetTag = data['counter']['target']
    counter = data['counter']['value']

    print ("timestamp: {}".format(ts))
    print ("geometry: {}".format(geo))
    print ("found: {} count: {}".format(targetTag, counter))

    #print (ngsiID)
    #print (ngsiType)
    #print (ts)
    #print (geo)

    ####Save img to file
    #fname = "test.jpg"
    #imgFile = open(fname, 'wb')
    #imgFile.write(byteImg)

    ####Move file to html deirectoy####
    #if os.path.exists(DIR+"test.jpg") == True:
    #    os.remove(DIR+"test.jpg")
    #shutil.move('./test.jpg', DIR)
    #####

    return data

def drawResults(data):

    byteImg = base64.b64decode(data['content']['value'].encode('utf-8'))

    with open("/var/www/html/app/"+outFileName+".jpg", "wb") as f:
        f.write(byteImg)

    img = cv2.imread("/var/www/html/app/"+outFileName+".jpg", 1)

    yolo = data['yolo']

    if yolo != "":

        for i in range(len(yolo)):
            left = int(yolo[i]['boundingBox']['left'])
            top = int(yolo[i]['boundingBox']['top'])
            width = int(yolo[i]['boundingBox']['width'])
            height = int(yolo[i]['boundingBox']['height'])
            tagName = yolo[i]['tagName']

            img = cv2.rectangle(img, (left, top), (left+width, top+height), (0, 255, 0), 3)
            cv2.putText(img, tagName, (left,top+20), font, font_size, (0, 255, 0))

    face = data['face']

    if face != "":

        for i in range(len(face)):
            left = int(face[i]['boundingBox']['left'])
            top = int(face[i]['boundingBox']['top'])
            width = int(face[i]['boundingBox']['width'])
            height = int(face[i]['boundingBox']['height'])

            img = cv2.rectangle(img, (left, top), (left+width, top+height), (255, 0, 0), 3)
 

    if os.path.exists("/var/www/html/app/"+outFileName+"_result.jpg") == True:
        os.remove("/var/www/html/app/"+outFileName+"_result.jpg")
    cv2.imwrite("/var/www/html/app/"+outFileName+"_result.jpg", img)


if __name__ == '__main__':

    while True:
        data = getData()
        drawResults(data)
        time.sleep(SLEEP)

