#import cefpyco
import time
import sys
import threading
import json
import os
import base64
import subprocess
#import netifaces as ni
from logging import basicConfig, getLogger, DEBUG, INFO

#import from tvFactoryLibrary
from common import common
#from protocol import icnCefore
from protocol import kafka
#from protocol import callSF
from service import mosaic
#######

SETTING = "./config/nodeSetting.json"
#SERVICEMAP = "./config/serviceMap.json"

if __name__ == '__main__':
    #args = sys.argv
    #common.checkARG(len(args))
    #interest = str(args[1])

    #interest = "kafka:/mosaic/yolotiny/labcam"
    #targetService = "yolotiny"
    #targetTag = "person"

    interest = os.environ['TOPIC']
    targetService = os.environ['SERVICE']
    targetTag = os.environ['TAG']
    funcList = common.analyzeInterest(interest)

    #if funcList[1] == "yolotiny":
    #    ARG = ["/src/darknet", "socket", "/src/cfg/yolov3-tiny.cfg", "/src/yolov3-tiny.weights"]
    #    subprocess.Popen(ARG)
    #    time.sleep(5)

    #set tvFactory parameters
    with open(SETTING, "r") as fp:
        setting = common.jsonReader(fp)

    #hostIP = ni.ifaddresses(setting["iface"])[ni.AF_INET][0]['addr']
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

                logger.info("[main] mode: service function mode")
                #request data to process data
                reqName = [funcList[0], funcList[2]]
                startTime = time.time()

                rxData = icnCefore.icnGetContentV2(handle, reqName, icnSetting)
                #rxData = icnCefore.icnGetContentV3(handle, reqName, icnSetting)

                timeIcnGet = common.outMmSec(startTime)
 
                qos = rxData["qos"]
                numSeg = rxData["numSeg"]
                rxData = rxData["payload"]

                #call service function
                startTime = time.time()
                #SERVICE = portmap[funcList[1]]

                #body = json.loads(rxData)
                #content = body['data'][contentName]['value']
                content = rxData

                ##### result is string
                result = mosaic.callMosaic(interest, rxData, targetService, targetTag)
                procData = json.dumps(result)

                ##### procData is JSON type (string)
                #if SERVICE["output"] == "marge":
                #    procData = callSF.concatData(rxData, result, funcList[1])
                #else:
                #   procData = result
                #######
                timeProc = common.outMmSec(startTime)


                #publish content
                reqName = [funcList[0], funcList[1] + "/" + funcList[2]]
                startTime = time.time()

                if (icnMode == "sync"):
                    #icn sync mode
                    icnCefore.syncIcnPubContentV2(handle, procData, reqName, icnSetting)
                    #icnCefore.syncIcnPubContentV3(handle, procData, reqName, icnSetting)
                else:
                    #icn async mode
                    icnCefore.asyncIcnPubContentV2(handle, procData, reqName, icnSetting)
                    #icnCefore.syncIcnPubContentV3(handle, procData, reqName, icnSetting)
               
                timeIcnPub = common.outMmSec(startTime)

                common.printExtractRawData(procData, interest)
                logger.info("[main] publish complete!")

                qosData = {"host": hostIP, "interest": funcList[0]+"/"+funcList[2], 
                            "qos": qos, "numSeg": numSeg,
                            "intRev": timeIntRev, "icnGet": timeIcnGet,
                            "proc": timeProc, "icnPub": timeIcnPub}

                logger.info("[main] performance {}".format(qosData))
                thread1 = threading.Thread(target=kafka.kafkaPubContent(kafkaBroker, json.dumps(qosData), TOPIC_OUT))

            if (icnMode != "sync"):
                time.sleep(SLEEP)


    if (funcList[0] == "kafka:"):

        logger.info("[main] kafka mode")

        #use controller broker for data plane

        while True:

            logger.info("[main] mode: service function mode")

            #request data to process data
            TOPIC_SUB = funcList[2]
            logger.info("[main] subscribe topic {}".format(TOPIC_SUB))
            consumer = kafka.kafkaSubContent(BROKER, TOPIC_SUB)

            startTime = time.time()

            for message in consumer:

                rxData = message.value.decode()
                timeKafkaGet = common.outMmSec(startTime)
 
                #qos = rxData["qos"]
                #numSeg = rxData["numSeg"]
                #rxData = rxData["payload"]

                #call service function
                startTime = time.time()
                #SERVICE = portmap[funcList[1]]

                #body = json.loads(rxData)
                #content = body['data'][contentName]['value']
                content = rxData

                ##### result is string
                result = mosaic.callMosaic(interest, rxData, targetService, targetTag)
                procData = json.dumps(result)

                ##### procData is JSON type (string)
                #if SERVICE["output"] == "marge":
                #    procData = callSF.concatData(rxData, result, funcList[1])
                #else:
                #    procData = result
                #######

                timeProc = common.outMmSec(startTime)

                #publish content
                TOPIC_PUB = funcList[1] + "_" + funcList[2]
                startTime = time.time()

                logger.info("[main] publish topic name {}".format(TOPIC_PUB))
                kafka.kafkaPubContent(kafkaBroker, procData, TOPIC_PUB)
               
                timeKafkaPub = common.outMmSec(startTime)

                common.printExtractRawData(procData, interest)
                logger.info("[main] publish complete!")

                #qosData = {"host": hostIP, "interest": funcList[0]+"/"+funcList[2], 
                #           "qos": qos, "numSeg": numSeg,
                #           "intRev": timeIntRev, "icnGet": timeIcnGet,
                #           "proc": timeProc, "icnPub": timeIcnPub}

                #logger.info("[main] performance {}".format(qosData))
                #thread1 = threading.Thread(target=kafka.kafkaPubContent(kafkaBroker, json.dumps(qosData), TOPIC_OUT))

 
