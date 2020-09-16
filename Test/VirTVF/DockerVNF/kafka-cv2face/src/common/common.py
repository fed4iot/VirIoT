import sys
import time
import json
import datetime
import base64
#import cv2
import os
from logging import getLogger

logger = getLogger(__name__)
serList = ["capImg", "yolo", "face", "counter", "finder"]

#font = cv2.FONT_HERSHEY_COMPLEX_SMALL
#font_size =1

def checkARG(num):

    if num != 2:
        print ("[Usage]: sudo python3 **.py [Interest/Topic]")
        print ("")
        print ("Available service list:")

        for i in range (len(serList)):
            print ("Service: {}".format(serList[i]))
            print ("")

            print ("[Interest]: ccn:/camera")
            print ("[Interest]: ccn:/yolo/camera")
            print ("[Interest]: ccn:/face/camera")
            print ("[Interest]: ccn:/counter/yolo/camera")
            print ("")
            
            print ("[Proxy]: ccn:/proxy/test")
            print ("")
            
            print ("[Topic]: kafka:/camera")
            print ("[Topic]: kafka:/yolo/camera")
            print ("[Topic]: kafka:/face/camera")
            print ("[Topic]: kafka:/counter/yolo/camera")
            sys.exit(1)


def analyzeInterest(interest):

    prefix = interest.split(':',2)

    if prefix[0] == "ccn":
        delimiter = "/"
    elif prefix[0] == "kafka":
        delimiter = "_"
        interest = interest.replace('/', '_')

    logger.debug("[analyzeInterest]: Mode is {}".format(prefix[0]))

    funcList = interest.split(delimiter,2)
	
    if len(funcList) == 3:
        PREFIX = funcList[0]
        FUNC = funcList[1]
        reqFUNC = funcList[2]
    elif len(funcList) == 2:
        PREFIX = funcList[0]
        FUNC = funcList[1]
        reqFUNC = ""
    else:
        logger.debug("[analyzeInterest] Error")
        sys.exit(1)

    funcList = [PREFIX, FUNC, reqFUNC]
    logger.debug("[analyzeInterest] {} {} {}".format(funcList[0], funcList[1], funcList[2]))
    return funcList


def analyzeKafkaTopic(topic):

    funcList = topic.split('_',2)
	
    if len(funcList) == 3:
        PREFIX = funcList[0]
        FUNC = funcList[1]
        reqFUNC = funcList[2]
    elif len(funcList) == 2:
        PREFIX = funcList[0]
        FUNC = funcList[1]
        reqFUNC = ""
    else:
        logger.debug("[analyzeKafkaTopic] Error")
        sys.exit(1)

    funcList = [PREFIX, FUNC, reqFUNC]
    logger.debug("[analyzeKafkaTopic] {} {} {}".format(funcList[0], funcList[1], funcList[2]))
    return funcList


def interestMode(funcList):

    if funcList[1] == "proxy":
        MODE = "proxy"
        funcList[1] = funcList[2]
        funcList[2] = ""
    else:
        MODE = "chain"

    if funcList[2] == "":
        reqName = [funcList[0], MODE, funcList[1] + "/" + funcList[2]]
    else:
        reqName = [funcList[0], MODE, funcList[1]]

    return reqName

def getContentName(interest):

    listName = interest.split("/")
    numName = len(listName)

    logger.debug("[getContentName] {}".format(listName))

    #last name is content name
    return listName[numName-1]

def outMmSec(startTime):
    return (time.time() - startTime)*1000


def outDuration(outString, startTime):

    nowTime = time.time()
    logger.debug("[log] {} {}".format(outString, nowTime-startTime))


def getQoS(startTime, startTime2, endTime, data):

    ts = datetime.datetime.now()
    unixtime = ts.timestamp()
    rtt = (endTime - startTime) * 1000 #(mc): including notify # of semgnets
    rtt2 = (endTime - startTime2) * 1000 #(mc): only for obtaining data
    dataSize = sys.getsizeof(data) * 8 #(bit)
    throughput = dataSize / rtt2 / 1000 #(Mbps): for obtaining data

    qos = {"ts": str(ts), "unix time": unixtime, "rtt(all)": rtt, 
           "rtt(data)": rtt2, "throughput": throughput, "data size": dataSize}

    logger.debug("[log] getQoS {}".format(qos))

    return qos

def jsonWriter(fp, data):

    json.dump(data, fp)
    logger.debug("[jsonWriter] JSON file is written")

def jsonReader(fp):

    jsonData = json.load(fp)
    return jsonData

def printExtractRawData(data, interest):

    temp = json.loads(data)
    name = getContentName(interest)
    temp[name].pop('content')

    print ("[log] publish data {}".format(temp))

def drawYOLO(img, data):

    temp = json.loads(data)

    if 'yolotiny' in temp:
        yolo = temp['yolotiny']
    elif 'yologpu' in temp:
        yolo = temp['yologpu']
    elif 'yolo' in temp:
        yolo = temp['yolo']

    if yolo != "":

        for i in range(len(yolo)):
            left = int(yolo[i]['boundingBox']['left'])
            right = int(yolo[i]['boundingBox']['top'])
            top = int(yolo[i]['boundingBox']['width'])
            bottom = int(yolo[i]['boundingBox']['height'])
            tagName = yolo[i]['tagName']

            #img = cv2.rectangle(img, (left, top), (right, bottom), (0, 255, 0), 3)
            #cv2.putText(img, tagName, (left,top+20), font, font_size, (0, 255, 0))

    return img

def drawFace(img, data):

    temp = json.loads(data)
    face = temp['face']

    if face != "":

        for i in range(len(face)):
            left = int(face[i]['faceRectangle']['left'])
            top = int(face[i]['faceRectangle']['top'])
            width = int(face[i]['faceRectangle']['width'])
            height = int(face[i]['faceRectangle']['height'])
            gender = face[i]['faceAttributes']['gender']
            age = face[i]['faceAttributes']['age']

            #img = cv2.rectangle(img,(left, top), (left+width, top+height), (255, 0, 0), 3)
            #cv2.putText(img, gender, (left, 20+top), font, font_size, (255,0,0))
            #cv2.putText(img, str(age), (left, 40+top), font, font_size, (255,0.0))

    return img


def imageWithResultWriter(data, interest):

    temp = json.loads(data)
    name = getContentName(interest)
    img = temp[name].pop('content')

    byteImg = base64.b64decode(img['value'].encode('utf-8'))

    with open("/var/www/html/tvf/"+name+".jpg", "wb") as f:
        f.write(byteImg)

    #img = cv2.imread("/var/www/html/tvf/"+name+".jpg", 1)

    if "crop" not in interest:
        if "yolo" in interest:
            img = drawYOLO(img, data)
        if "face" in interest:
            img = drawFace(img, data)
    os.remove("/var/www/html/tvf/"+name+"_result.jpg")
    #cv2.imwrite("/var/www/html/tvf/"+name+"_result.jpg", img)

def imageWriter(data, interest):

    temp = json.loads(data)
    name = getContentName(interest)
    img = temp[name].pop('content')

    if type(img['value']) is list:

        for i in range(len(img['value'])):
            byteImg = base64.b64decode(img['value'][i].encode('utf-8'))

            with open(name+"_"+str(i)+".jpg", "wb") as f:
                f.write(byteImg)
    else:
        byteImg = base64.b64decode(img['value'].encode('utf-8'))

        with open(name+".jpg", "wb") as f:
            f.write(byteImg)

