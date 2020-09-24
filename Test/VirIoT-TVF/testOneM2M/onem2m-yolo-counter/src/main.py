import requests
import json
import base64
import time
import sys
import ast
import os
import shutil
import uuid
import socket
import subprocess
import cv2

SLEEP = 2

### OneM2M Broker ###
BROKER = ""
PORT = ""
baseURI = "http://" + BROKER + ":" + PORT +"/onem2m/"
API = "latest"
headers = {'Content-Type':'application/vnd.onem2m-res+json',}
###

### OneM2M Resource ###
RN = ["waseda", "netcam"]
RN2 = ["waseda", "counter"]
###

### HTML deirectory ###
DIR ="/var/www/html/app/"
###

### For YOLO
HOST = "0.0.0.0"
PORT = 33101
REVSIZE = 1024
###

### For count objects
TAG = "person"
###

### For face detection
face_cascade_name = cv2.data.haarcascades+"haarcascade_frontalface_default.xml"
#eye_cascade_name = cv2.data.haarcascades+"haarcascade_eye_tree_eyeglasses.xml"
###


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
    #ts = data['timestamp']
    #byteImg = base64.b64decode(data['content']['value'].encode('utf-8'))
    #geo = data['geometry']

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

def callYOLO(data):

    print ("[callYOLO] start callYOLO function")

    host = HOST
    port = int(PORT)
    revSize = int(REVSIZE)

    #extract image
    byteImg = base64.b64decode(data['content']['value'].encode('utf-8'))

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:

        s.connect((host, port))

        #sending input data
        if byteImg != b'':
            s.sendall(byteImg)
            s.shutdown(1)
        ########

        #receiving data from service function
        revData = b''
        data = s.recv(revSize)
        revData += data

        if sys.getsizeof(data) > revSize:

            while True:
                data = s.recv(revSize)
                if not data:
                    break
                revData += data

        result = revData.decode()

        YOLO = []
        if (result != "null"):

            temp = result.split("_")
            numDetect = len(temp)

            for i in range(numDetect-1):

                temp2 = temp[i].split(",")

                left = int(temp2[2])
                right = int(temp2[3])
                top = int(temp2[4])
                bottom = int(temp2[5])
                width = right - left
                height = bottom - top

                dict_body = {'tagName': temp2[0],
                             'tagID': str(uuid.uuid4()),
                             'probability': float(temp2[1])/100.0,
                             'boundingBox': {'left': left,
                                             'top': top,
                                             'width': width,
                                             'height': height
                                            }
                            }
                YOLO.append(dict_body)

        result = {"yolo": YOLO}
        #########

        print (result)

        return result

def callObjectCounter(data, targetTag):

    data = data['yolo']
    count = 0

    for i in range(len(data)):
        if (data[i]['tagName'] == targetTag):
            count = count + 1

    #data model
    body = {
            'counter': {'type': 'Property', 'target': targetTag, 'value': count}
           }

    print (body)

    return body


def callCV2Face(data):

    byteImg = base64.b64decode(data['content']['value'].encode('utf-8'))

    with open('temp.jpg', 'wb') as f:
        f.write(byteImg)
    srcImg = cv2.imread('temp.jpg', 1)

    face_cascade = cv2.CascadeClassifier(face_cascade_name)
    faces = face_cascade.detectMultiScale(srcImg)

    FACE = []

    for (x, y, w, h) in faces:
        bbox = {"boundingBox": {'left': str(x),
                                'top': str(y),
                                'width': str(w),
                                'height': str(h)
                                }
                }

        FACE.append(bbox)

    result = {"face": FACE}
    os.remove('temp.jpg')

    print (result)

    return result


if __name__ == '__main__':

    ARG = ["./darknet", "socket", "./cfg/yolov3-tiny.cfg", "./yolov3-tiny.weights"]
    #for full spec of YOLO
    #ARG = ["./darknet", "socket", "./cfg/yolov3.cfg", "./yolov3.weights"]

    subprocess.Popen(ARG)
    time.sleep(5)
    #time.sleep(15)

    #OneM2M data format

    aeBody = { "m2m:ae":{
                    "rn": RN2[0],
                    "api": "placeholder",
                    "rr": "TRUE"
                    }
            }

    cntBody = { "m2m:cnt": {
                    "rn": RN2[1]
                    }
                }

    #Create oneM2M resource
    response = requests.post(baseURI, headers=headers, data=json.dumps(aeBody))
    print ("onem2m app resource create: {}".format(response))

    response = requests.post(baseURI+RN2[0]+"/", headers=headers, data=json.dumps(cntBody))
    print ("onem2m container resource create: {}".format(response))
    #####

    while True:
        data = getData()
        yolo_result = callYOLO(data)
        count_result = callObjectCounter(yolo_result, TAG)
        face_result = callCV2Face(data)

        data.update(yolo_result)
        data.update(count_result)
        data.update(face_result)

        #OneM2M data format
        body = {"m2m:cin": {
                "con": data,
                "cnf": "text/plain:0"
                    }
                }
        #####

        end_point = baseURI + RN2[0] + "/" + RN2[1] + "/"
        response = requests.post(end_point, headers=headers, data=json.dumps(body))
        print("[httpPublish] data publish to onem2m broker: {}".format(response))
        print("[httpPublish] publish complete!")

        time.sleep(SLEEP)

