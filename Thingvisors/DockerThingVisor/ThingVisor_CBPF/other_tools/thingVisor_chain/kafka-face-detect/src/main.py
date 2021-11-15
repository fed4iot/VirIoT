#import cefpyco
import time
import sys
import threading
import json
import os
import base64
import subprocess
import datetime
import uuid
#import netifaces as ni
from logging import basicConfig, getLogger, DEBUG, INFO

#import from tvFactoryLibrary
from common import common
#from protocol import icnCefore
from protocol import kafka
from service import face_detect
#######

SETTING = "./config/nodeSetting.json"
#SERVICEMAP = "./config/serviceMap.json"

def convertTime(timestamp):

    return timestamp.strftime('%Y-%m-%dT%H:%M:%S.%fZ')


def actuateFromController(CONTROL, TOPIC_IN, ID, kafkaBroker, consumer):

    print ("run actuation process")
    controller = kafka.kafkaSubContent(CONTROL, TOPIC_IN)

    for message in controller:

        control_message = message.value.decode()
        control_message = json.loads(control_message)

        print (control_message)

        if UUID == control_message['uuid']:
            if 'feedback' in control_message:
                message = control_message['feedback']
                if message == 'termination':
                    #kafkaBroker.close()
                    os.environ['KILLSWITCH'] = 'on'
                    print ('close kafka broker')


if __name__ == '__main__':
    #args = sys.argv
    #common.checkARG(len(args))

    #os.environ['TOPIC'] = "kafka:/humandetector/tokyo.01"
    #os.environ['TAG'] = "person"
    #os.environ['TAR'] = "yolo"
    #os.environ['BROKER'] = ''
    #os.environ['CONTROL'] = ''
    #os.environ['SERVICE'] = 'humandetector'
    #os.environ['CLUSTER'] = 'slab'
    #os.environ['PROTOCOL'] = 'kafka'
    #os.environ['ID'] = 'test'
    #os.environ['NAMESPACE'] = 'test'
    os.environ['KILLSWITCH'] = 'off'

    interest = os.environ['TOPIC']
    #targetTag = os.environ['TAG']
    #targetSer = os.environ['TAR']
    BROKER = os.environ['BROKER']
    CONTROL = os.environ['CONTROL']
    SERVICE = os.environ['SERVICE']
    CLUSTER = os.environ['CLUSTER']
    PROTOCOL = os.environ['PROTOCOL']
    UUID = os.environ['ID']
    NAMESPACE = os.environ['NAMESPACE']

    targetTag = ""
    targetSer = ""

    funcList = common.analyzeInterest(interest)

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
    TOPIC_OUT = setting["topic to controller"]
    TOPIC_IN = setting["topic from controller"]
    HOST = setting["host"]
    #revSize = setting["revSize"]
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
    kafkaController = kafka.kafkaConnect(CONTROL)
    #UUID = uuid.uuid4()

    #run feedback monitor process
    #actuator_thread = threading.Thread(target=actuateFromController,
    #        args=([CONTROL, TOPIC_IN, UUID, kafkaBroker]))
    #actuator_thread.setDaemon(True)
    #actuator_thread.start()

    if (funcList[0] == "ccn:"):

        logger.info("[main] ccn (cefore) mode")

        with cefpyco.create_handle() as handle:

            while True:

                logger.info("[main] mode: service function mode")
                #request data to process data
                reqName = [funcList[0], funcList[2]]

                start_get = datetime.datetime.now()

                rxData = icnCefore.icnGetContentV2(handle, reqName, icnSetting)
                #rxData = icnCefore.icnGetContentV3(handle, reqName, icnSetting)
                end_get = datetime.datetime.now()

                #timeIcnGet = common.outMmSec(startTime)

                qos = rxData["qos"]
                numSeg = rxData["numSeg"]
                rxData = rxData["payload"]

                get_size = sys.getsizeof(rxData)

                #call service function
                start_sf = datetime.datetime.now()
                #SERVICE = portmap[funcList[1]]

                #body = json.loads(rxData)
                #content = body['data'][contentName]['value']

                ##### result is string
                procData = mosaic.callMosaic(interest, rxData, targetTag)
                procData = json.dumps(procData)
                #######

                end_sf = datetime.datetime.now()
                pub_size = sys.getsizeof(procData)

                #publish content
                reqName = [funcList[0], funcList[1] + "/" + funcList[2]]
                start_pub = datetime.datetime.now()

                if (icnMode == "sync"):
                    #icn sync mode
                    icnCefore.syncIcnPubContentV2(handle, procData, reqName, icnSetting)
                    #icnCefore.syncIcnPubContentV3(handle, procData, reqName, icnSetting)
                else:
                    #icn async mode
                    icnCefore.asyncIcnPubContentV2(handle, procData, reqName, icnSetting)
                    #icnCefore.syncIcnPubContentV3(handle, procData, reqName, icnSetting)
               
                end_pub = datetime.datetime.now()

                common.printExtractRawData(procData, interest)
                logger.info("[main] publish complete!")

                time_get = (end_get - start_get).total_seconds()
                time_sf = (end_sf - start_sf).total_seconds()
                time_pub = (end_pub - start_pub).total_seconds()
    
                sf_log = {"node id": str(UUID), "service id": funcList[1], "service name": SERVICE, "cluster": CLUSTER,
                        "interest": {"in": funcList[2], "out": funcList[1]+"/"+funcList[2]}, "protocol": PROTOCOL,
                        "timestamp": {"in": str(end_get), "out": str(end_pub)},
                        "delay": {"get time": time_get, "proc time": time_sf, "pub time": time_pub},
                        "data size": {"get size": get_size, "pub size": pub_size},
                        "namespace": NAMESPACE
                        }

                sf_log = json.dumps(sf_log)

                #logger.info("[main] performance {}".format(qosData))
                thread1 = threading.Thread(target=kafka.kafkaPubContent, args=([kafkaController, sf_log, TOPIC_OUT]))
                thread1.start()
            if (icnMode != "sync"):
                time.sleep(SLEEP)


    if (funcList[0] == "kafka:"):

        logger.info("[main] kafka mode")

        #use controller broker for data plane

        logger.info("[main] mode: service function mode")

        #request data to process data
        TOPIC_SUB = funcList[2]
        logger.info("[main] subscribe topic {}".format(TOPIC_SUB))
        consumer = kafka.kafkaSubContent(BROKER, TOPIC_SUB)

        #run feedback monitor process
        actuator_thread = threading.Thread(target=actuateFromController,
            args=([CONTROL, TOPIC_IN, UUID, kafkaBroker, consumer]))
        actuator_thread.setDaemon(True)
        actuator_thread.start()

        UTC = datetime.timezone.utc

        while True:

            #logger.info("[main] mode: service function mode")

            #request data to process data
            #TOPIC_SUB = funcList[2]
            #logger.info("[main] subscribe topic {}".format(TOPIC_SUB))
            #consumer = kafka.kafkaSubContent(BROKER, TOPIC_SUB)

            #start_get = datetime.datetime.now(UTC)
            #counter = 0

            for message in consumer:

                if os.environ['KILLSWITCH'] == 'on':
                    consumer.close()
                    kafkaBroker.close()

                #if counter != 0:
                #    start_get = end_get
                #else:
                #    counter = 1

                rxData = message.value.decode()
                rxData = json.loads(rxData)
                end_get = datetime.datetime.now(UTC)
                in_metric = consumer.metrics()
                get_size = sys.getsizeof(rxData)

                ### extract timestamp
                #tar_name = interest.split('/')[2]
                tx_ts = rxData['msg']['createdAt']['value']
                start_get = datetime.datetime.strptime(tx_ts, '%Y-%m-%dT%H:%M:%S.%fZ').replace(tzinfo=datetime.timezone.utc)
                ###

                #call service function
                start_sf = datetime.datetime.now(UTC)
                ARGS = {'target tag': targetTag, 'target service': targetSer}

                procData = face_detect.callService(interest, rxData, ARGS)

                end_sf = datetime.datetime.now(UTC)
                #pub_size = sys.getsizeof(procData)

                #publish content
                TOPIC_PUB = funcList[1] + "_" + funcList[2]
                start_pub = datetime.datetime.now(UTC)
                #procData[funcList[1]].update({'id': str(UUID), 'timestamp': convertTime(start_pub)})
                procData = json.dumps(procData)
                pub_size = sys.getsizeof(procData)

                if os.environ['KILLSWITCH'] != 'on':
                    logger.info("[main] publish topic name {}".format(TOPIC_PUB))
                    out_metric = kafka.kafkaPubContent(kafkaBroker, procData, TOPIC_PUB)
               
                end_pub = datetime.datetime.now(UTC)

                #print (procData)
                #common.printExtractRawData(procData, interest)
                logger.info("[main] publish complete!")

                time_get = (end_get - start_get).total_seconds()
                time_sf = (end_sf - start_sf).total_seconds()
                time_pub = (end_pub - start_pub).total_seconds()
    
                sf_log = {"node id": str(UUID), "service id": funcList[1], "service name": SERVICE, "cluster": CLUSTER,
                        "interest": {"in": funcList[2], "out": funcList[1]+"_"+funcList[2]}, "protocol": PROTOCOL,
                        "timestamp": {"in": convertTime(end_get), "out": convertTime(end_pub)},
                        "delay": {"get time": time_get, "proc time": time_sf, "pub time": time_pub},
                        "data size": {"get size": get_size, "pub size": pub_size},
                        "metric": {"in": in_metric, "out": out_metric},
                        "namespace": NAMESPACE
                         }
 
                #sf_log = json.dumps(sf_log)

                to_logger = {"id": str(UUID), "type": "log", "name": TOPIC_OUT, "timestamp": convertTime(end_get), "content": sf_log}
                to_logger = json.dumps(to_logger)

                #logger.info("[main] performance {}".format(qosData))
                thread1 = threading.Thread(target=kafka.kafkaPubContent, args=([kafkaController, to_logger, TOPIC_OUT]))
                thread1.start()
