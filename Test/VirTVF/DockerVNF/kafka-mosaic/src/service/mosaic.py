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

RATIO = 0.05
CODEC = 'jpg'
QUALITY = 95
CODEC = 'jpg'

def mosaic(src, ratio):

    small = cv2.resize(src, None, fx=ratio, fy=ratio, interpolation=cv2.INTER_NEAREST)

    return cv2.resize(small, src.shape[:2][::-1], interpolation=cv2.INTER_NEAREST)

def mosaic_area(src, x, y, width, height, ratio):

    dst = src.copy()
    dst[y:y + height, x:x + width] = mosaic(dst[y:y + height, x:x + width], ratio)

    return dst

def encode(img, codec):

    if codec == "jpg":
        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), QUALITY]
        result, encImg = cv2.imencode(".jpg", img, encode_param)

    if codec == "png":
        encode_param = [int(cv2.IMWRITE_PNG_QUALITY), QUALITY]
        result, encImg = cv2.imencode(".png", img, encode_param)

    return encImg

def callMosaic(interest, rxData, targetService, targetTag):

    rxData = json.loads(rxData)
    content = common.getContentName(interest)
    temp = rxData[content]['content']['value']
    byteImg = base64.b64decode(temp.encode('utf-8'))
    codec = CODEC

    with open('temp.jpg', 'wb') as f:
        f.write(byteImg)
    srcImg = cv2.imread('temp.jpg', 1)

    data = rxData[targetService]

    key = "boundingBox"

    for i in range(len(data)):
        if (data[i]['tagName'] == targetTag):
            left = int(data[i][key]['left'])
            top = int(data[i][key]['top'])
            width= int(data[i][key]['width'])
            height = int(data[i][key]['height'])

            #mosaic
            srcImg = mosaic_area(srcImg, left, top, width, height, RATIO)

    encImg = encode(srcImg, codec)
    DATA = base64.b64encode(encImg).decode('utf-8')
    rxData[content]['content']['value'] = DATA

    serviceName = common.analyzeInterest(interest)[1]
    
    #meta data
    body = {'id': serviceName + ':' + targetService + ':' + targetTag,
            'type': 'service function'}

    rxData.update({serviceName: body})

    os.remove('temp.jpg')
    return rxData
