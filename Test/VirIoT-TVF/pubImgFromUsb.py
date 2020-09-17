import cefpyco
import time
import sys
import threading
import json
import os
import base64
import netifaces as ni
import gphoto2 as gp
import cv2
from logging import basicConfig, getLogger, DEBUG, INFO

#import from tvFactoryLibrary
from common import common
from protocol import icnCefore
from protocol import kafka
from protocol import callSF
#######

#DEV = "USBCAM"
DEV = "THETA"

SETTING = "./config/nodeSetting.json"
SERVICEMAP = "./config/serviceMap.json"

location = "waseda"
devType = "usb camera"
geometry = {"type": "Point", "coordinates": [35.7056, 129.708399]}
codec = "jpg"
quality =95
width = 1920
height = 1080
devID = 0

RMFLAG = 1

def callCapImgFromUsbCam(reqName):

    cam = cv2.VideoCapture(0)
    cam.set(3, width)
    cam.set(4, height)
    print ("[callServiceFunction] camera is ready")

    print ("[callServiceFunction] capture one frame")
    ret, frame = cam.read()

    if codec == "jpg":
        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), quality]
        result, encImg = cv2.imencode(".jpg", frame, encode_param)

    if codec == "png":
        encode_param = [int(cv2.IMWRITE_PNG_QUALITY), quality]
        result, encImg = cv2.imencode(".png", frame, encode_param)

    print ("[callServiceFunction] jpeg encode complete")

    binImg = base64.b64encode(encImg).decode('utf-8')

    print ("[callServiceFunction] base64 encode complete")

    content = {"id": location + ":" + reqName, "type": devType,
               "content": {"type": "Property", "value": binImg},
               "geometry": geometry}

    BODY = {reqName: content}
    BODY = json.dumps(BODY)

    print ("[callServiceFunction] capture complete")

    return BODY


def callCapImgFromTheta(reqName):

    camera = gp.Camera()
    camera.init()
    print ('[callCapTheta] Capture image')

    filePath = camera.capture(gp.GP_CAPTURE_IMAGE)
    tarPath = os.path.join('.', filePath.name)
    print ('[callCapTheta] Copying image to ', tarPath)

    cameraFile = camera.file_get(filePath.folder, filePath.name, gp.GP_FILE_TYPE_NORMAL)
    cameraFile.save(tarPath)

    camera.exit()

    #read image file
    with open(tarPath, 'rb') as f:
        img = f.read()

    binImg = base64.b64encode(img).decode('utf-8')

    content = {"id": location + ":" + reqName, "type": devType,
               "content": {"type": "Property", "value": binImg},
               "geometry": geometry}

    BODY = {reqName: content}

    BODY = json.dumps(BODY)

    print ("[callCapTheta] done!")

    if RMFLAG == 1:
        os.remove(tarPath)

    return BODY


if __name__ == '__main__':
    args = sys.argv
    common.checkARG(len(args))
    interest = str(args[1])
    funcList = common.analyzeInterest(interest)

    #set tvFactory parameters
    with open(SETTING, "r") as fp:
        setting = common.jsonReader(fp)

    hostIP = ni.ifaddresses(setting["iface"])[ni.AF_INET][0]['addr']
    MODE = setting["mode"]
    SLEEP = int(setting["sleep"])/1000 #(sec)
    CACHETIME = int(setting["cache time"]) #(msec)
    EXPIRY = int(setting["expiry"]) #(msec)
    TIMEOUT = int(setting["timeout"]) #(msec)
    segSize = int(setting["segSize"])
    icnMode = setting["icnMode"]
    BROKER = setting["broker"]
    TOPIC_OUT = setting["topic to controller"]
    TOPIC_IN = setting["topic from controller"]
    HOST = setting["host"]
    revSize = setting["revSize"]
    logLevel = setting["logLevel"]

    if (logLevel == "info"):
        basicConfig(level=INFO)
    if (logLevel == "debug"):
        basicConfig(level=DEBUG)
    logger = getLogger(__name__)
 
    icnSetting = {"segSize":segSize, "cacheTime":CACHETIME, "expiry":EXPIRY, "timeout":TIMEOUT}

    #read port mapping table
    #with open(SERVICEMAP, "r") as fp:
    #    portmap = common.jsonReader(fp)

    #set init value for log
    timeIntRev = 0
    timeIcnGet = 0
    timeProc = 0
    timeIcnPub = 0

    logger.info("[main] input interest name: {}".format(funcList))

    logger.info("[main] {}".format(icnSetting))
    logger.info("[main] icnMode:{}".format(icnMode))

    #connect kafka broker for control plane
    kafkaBroker = kafka.kafkaConnect(BROKER)

    if (funcList[0] == "ccn:"):

        logger.info("[main] ccn (cefore) mode")

        with cefpyco.create_handle() as handle:

            while True:

                logger.info("[main] mode: simple producer mode")

                startTime = time.time()
                
                if DEV == "THETA":
                    result = callCapImgFromTheta(funcList[1])
                if DEV == "USBCAM":
                    result = callCapImgFromUsbCam(funcList[1])
                timeProc = common.outMmSec(startTime)

                #publish content
                reqName = [funcList[0], funcList[1]]
                startTime = time.time()
                
                if (icnMode == "sync"):
                    #icn sync mode
                    icnCefore.syncIcnPubContentV2(handle, result, reqName, icnSetting)
                    #icnCefore.syncIcnPubContentV3(handle, result, reqName, icnSetting)
                else :
                    #icn async mode
                    icnCefore.asyncIcnPubContentV2(handle, result, reqName, icnSetting)
                    #icnCefore.asyncIcnPubContentV3(handle, result, reqName, icnSetting)

                
                timeIcnPub = common.outMmSec(startTime)

                common.printExtractRawData(result, funcList[1])
                logger.info("[main] publish complete!")

                time.sleep(SLEEP)

    if (funcList[0] == "kafka:"):

        logger.info("[main] kafka mode")

        #use controller broker for data plane

        while True:

            logger.info("[main] mode: simple publisher mode")

            startTime = time.time()

            if DEV == "THETA":
                result = callCapImgFromTheta(funcList[1])
            if DEV == "USBCAM":
                result = callCapImgFromUsbCam(funcList[1])
            timeProc = common.outMmSec(startTime)

            #publish content
            TOPIC_PUB = funcList[1]
            startTime = time.time()
                
            #print (sys.getsizeof(result))
            kafka.kafkaPubContent(kafkaBroker, result, TOPIC_PUB)
                
            timeKafkaPub = common.outMmSec(startTime)

            common.printExtractRawData(result, funcList[1])
            logger.info("[main] publish complete!")

            time.sleep(SLEEP)
 
