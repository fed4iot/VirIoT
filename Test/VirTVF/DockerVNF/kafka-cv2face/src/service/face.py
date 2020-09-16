import sys
import time
import json
import os
import cv2
import base64
from logging import basicConfig, getLogger, DEBUG, INFO

#import from tvFactoryLibrary
from common import common
#from protocol import icnCefore
#from protocol import kafka
#####

face_cascade_name = cv2.data.haarcascades+"haarcascade_frontalface_default.xml"
#eye_cascade_name = cv2.data.haarcascades+"haarcascade_eye_tree_eyeglasses.xml"

def cv2face(img):

    face_cascade = cv2.CascadeClassifier(face_cascade_name)
    faces = face_cascade.detectMultiScale(img)

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
    print (result)

    return result

def callCV2Face(interest, rxData):

    rxData = json.loads(rxData)
    content = common.getContentName(interest)
    temp = rxData[content]['content']['value']
    byteImg = base64.b64decode(temp.encode('utf-8'))

    with open('temp.jpg', 'wb') as f:
        f.write(byteImg)
    srcImg = cv2.imread('temp.jpg', 1)

    result = cv2face(srcImg)

    serviceName = common.analyzeInterest(interest)[1]
    
    rxData.update(result)

    os.remove('temp.jpg')
    return rxData
