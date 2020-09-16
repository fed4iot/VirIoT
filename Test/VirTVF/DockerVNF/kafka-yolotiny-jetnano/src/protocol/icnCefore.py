import cefpyco
import re
import base64
import json
import ast
import time
import subprocess
from logging import getLogger

#import from tvFactory Library
from common import common
#######

logger = getLogger(__name__)

PROTOCOL = "udp"

#beta version
#########################################################################
#get content using ICN protocol
#no more use notify interest
def icnGetContentV3(handle, reqName, setting):

    segSize = setting["segSize"]
    cacheTime = setting["cacheTime"]
    TIMEOUT = setting["timeout"]

    #reqName[0]: prefix (ccn:)
    #reqName[1]: interest name
    INT_CONTENT = reqName[0] + "/" + reqName[1]
    receive_data = b""

    while True:
        #start time for sending interest including segment size notification
        startTime = time.time()
        handle.send_interest(INT_CONTENT, 0, lifetime=TIMEOUT)
        logger.debug("[icnGetContent] send interest: {}".format(INT_CONTENT))

        info = handle.receive(timeout_ms=TIMEOUT)

        startTime2 = time.time()
        if info.is_succeeded and (info.name == INT_CONTENT) and (info.chunk_num == 0):

            receive_data = info.payload
            final_chunk_num = info.end_chunk_num
            logger.info("[icnGetContent] last num of segments: {}".format(final_chunk_num))

            if final_chunk_num != 0:
                #continue to request segments by sengind interest
                for i in range (final_chunk_num):
                    handle.send_interest(INT_CONTENT, i+1)
                    logger.debug("[icnGetContent] send Interst: {}".format(INT_CONTENT + "/" + str(i+1)))

                for i in range(final_chunk_num):
                    #receiving data corresponding to the interest
                    info = handle.receive()
                    if info.is_succeeded and (info.name == INT_CONTENT) and (info.chunk_num == i+1):
                        receive_data = receive_data + info.payload
                        logger.debug("[icnGetContent] received segment ID: {}".format(str(i+1)))


            logger.debug("[icnGetContent] receive complete!")

            #end time for obtaining data
            endTime = time.time()
            qos = common.getQoS(startTime, startTime2, endTime, receive_data)
            break

    payload = receive_data.decode('utf-8')
    dict_revData = {"qos": qos, "numSeg": int(final_chunk_num), "payload": payload}

    return dict_revData


#Synchronization mode: (synchronize between Publisher and Consumer)
#no more use notify interest
def syncIcnPubContentV3(handle, content, reqName, setting):

    segSize = setting["segSize"]
    cacheTime = setting["cacheTime"]
    expiry = setting["expiry"]
    TIMEOUT = setting["timeout"]

    content = content.encode('utf-8')

    #calculate required number of segments
    txSize = len(content)
    segNum = ((txSize -1) // segSize) + 1
    logger.info("[icnPubContent] required number of segments: {}".format(str(segNum)))

    txChunk = []

    for i in range(segNum):
        offset = i * segSize
        txChunk.insert(i, content[offset:offset + segSize])

    #define notify interest name
    #reqName[0]: prefix (ccn:)
    #reqName[1]: interest name
    INT_CONTENT = reqName[0] + "/" + reqName[1]
    handle.register(INT_CONTENT)
    logger.debug("[icnPubContent] waiting for the notify packet: {}".format(INT_CONTENT))

    while True:
        info = handle.receive()
        if info.is_succeeded and info.name == INT_CONTENT:
            #logger.debug("[icnPubContent] receive interest: {}".format(info))
            i = info.chunk_num
            handle.send_data(INT_CONTENT, txChunk[i], i, end_chunk_num=(segNum-1), expiry=expiry, cache_time=cacheTime)
            logger.debug("[icnPubContent] send chunk num: {}".format(str(i)))

        if i == (segNum-1):
            logger.debug("[icnPubContent] complete!")
            break

#Asynchronization mode (Publisher just publishes content to the CS)
def asyncIcnPubContentV3(handle, content, reqName, setting):

    segSize = setting["segSize"]
    cacheTime = setting["cacheTime"]
    expiry = setting["expiry"]
    TIMEOUT = setting["timeout"]

    logger.debug("[icnPubContent] {} {} {}".format(segSize, cacheTime, TIMEOUT))

    content = content.encode('utf-8')

    #calculate required number of segments
    txSize = len(content)
    segNum = ((txSize -1) // segSize) + 1
    logger.info("[icnPubContent] required number of segments: {}".format(str(segNum)))

    txChunk = []

    for i in range(segNum):
        offset = i * segSize
        txChunk.insert(i, content[offset:offset + segSize])

    #define notify interest name
    #reqName[0]: prefix (ccn:)
    #reqName[1]: interest name
    INT_CONTENT = reqName[0] + "/" + reqName[1]
    logger.debug("[icnPubContent] interest message: {}".format(INT_CONTENT))
    handle.register(INT_CONTENT)

    for i in range(segNum):
        handle.send_data(INT_CONTENT, txChunk[i], i, end_chunk_num=segNum-1, expiry=expiry, cache_time=cacheTime)
        logger.debug("[icnPubContent] send chunk num {}".format(str(i)))

    logger.info("[icnPubContent] complete!")

#########################################################################
#########################################################################

#########################################################################
#########################################################################
####stable version


#get content using ICN protocol
#no more use notify interest
def icnGetContentV2(handle, reqName, setting):

    segSize = setting["segSize"]
    cacheTime = setting["cacheTime"]
    TIMEOUT = setting["timeout"]

    #reqName[0]: prefix (ccn:)
    #reqName[1]: interest name
    INT_CONTENT = reqName[0] + "/" + reqName[1]
    receive_data = b""

    while True:
        #start time for sending interest including segment size notification
        startTime = time.time()
        handle.send_interest(INT_CONTENT, 0, lifetime=TIMEOUT)
        logger.debug("[icnGetContent] send interest: {}".format(INT_CONTENT))
    
        info = handle.receive(timeout_ms=TIMEOUT)
        #logger.debug("[icnGetContent] waiting chain notification: {}".format(INT_CONTROL))

        startTime2 = time.time()
        if info.is_succeeded and (info.name == INT_CONTENT) and (info.chunk_num == 0):

            receive_data = info.payload
            num_segments = info.end_chunk_num
            logger.info("[icnGetContent] last num of segments: {}".format(num_segments))

            if num_segments != 0:
                #continue to request segments by sengind interest
                i=1
                while i <= num_segments:
                    while True:
                        handle.send_interest(INT_CONTENT, i)
                        #print ("[icnGetContent] send Interst: {}".format(INT_CONTENT + "/" + str(i)))
                
                        #receiving data corresponding to the interest
                        info = handle.receive()
                        if info.is_succeeded and (info.name == INT_CONTENT) and (info.chunk_num == i):
                            receive_data = receive_data + info.payload
                            #print ("[icnGetContent] received segment ID: {}".format(str(i)))
                            i=i+1
                        break

            logger.debug("[icnGetContent] receive complete!")

            #end time for obtaining data
            endTime = time.time()
            qos = common.getQoS(startTime, startTime2, endTime, receive_data)
            break

    payload = receive_data.decode('utf-8')
    dict_revData = {"qos": qos, "numSeg": int(num_segments), "payload": payload}

    return dict_revData


#get content using ICN protocol
#old version. please do not use this function
def icnGetContent(handle, reqName, setting):

    segSize = setting["segSize"]
    cacheTime = setting["cacheTime"]
    TIMEOUT = setting["timeout"]

    #reqName[0]: prefix (ccn:)
    #reqName[1]: chain or proxy
    #reqName[2]: interest name
    INT_CONTROL = reqName[0] + "/" + reqName[1] + "/" + reqName[2]

    while True:
        #start time for sending interest including segment size notification
        startTime = time.time()
        handle.send_interest(INT_CONTROL, 0, lifetime=TIMEOUT)
        logger.debug("[icnGetContent] send interest: {}".format(INT_CONTROL))
    
        info = handle.receive(timeout_ms=TIMEOUT)
        logger.debug("[icnGetContent] waiting chain notification: {}".format(INT_CONTROL))

        if info.is_succeeded and (info.name == INT_CONTROL) and (info.chunk_num == 0):

            num_segments = info.payload_s
            logger.info("[icnGetContent] required num of segments: {}".format(num_segments))

            #sending interest packets
            INT_CONTENT = reqName[0] + "/" + reqName[2]
            receive_data = b""

            #start time for obtaining data
            startTime2 = time.time()
            for i in range(int(num_segments)):
                while True:
                    handle.send_interest(INT_CONTENT, i)
                    #print ("[icnGetContent] send Interst: {}".format(INT_CONTENT + "/" + str(i)))
                
                    #receiving data corresponding to the interest
                    info = handle.receive()
                    if info.is_succeeded and (info.name == INT_CONTENT) and (info.chunk_num == i):
                        receive_data = receive_data + info.payload
                        #print ("[icnGetContent] received segment ID: {}".format(str(i)))
                        break

            logger.debug("[icnGetContent] receive complete!")

            #end time for obtaining data
            endTime = time.time()
            qos = common.getQoS(startTime, startTime2, endTime, receive_data)
            break

    payload = receive_data.decode('utf-8')
    dict_revData = {"qos": qos, "numSeg": int(num_segments), "payload": payload}

    return dict_revData
########

#Synchronization mode: (synchronize between Publisher and Consumer)
#no more use notify interest
def syncIcnPubContentV2(handle, content, reqName, setting):

    segSize = setting["segSize"]
    cacheTime = setting["cacheTime"]
    expiry = setting["expiry"]
    TIMEOUT = setting["timeout"]

    content = content.encode('utf-8')

    #calculate required number of segments
    txSize = len(content)
    segNum = ((txSize -1) // segSize) + 1
    logger.info("[icnPubContent] required number of segments: {}".format(str(segNum)))

    txChunk = []

    for i in range(segNum):
        offset = i * segSize
        txChunk.insert(i, content[offset:offset + segSize])

    #define notify interest name
    #reqName[0]: prefix (ccn:)
    #reqName[1]: interest name
    INT_CONTENT = reqName[0] + "/" + reqName[1]
    handle.register(INT_CONTENT)
    logger.debug("[icnPubContent] waiting for the notify packet: {}".format(INT_CONTENT))

    while True:
        info = handle.receive()
        if info.is_succeeded and info.name == INT_CONTENT and info.chunk_num == 0:

            handle.send_data(INT_CONTENT, txChunk[0], 0, end_chunk_num=(segNum-1), expiry=expiry, cache_time=cacheTime)
            logger.debug("[icnPubContent] send content and end chunk num {}".format(str(segNum-1)))

        elif info.is_succeeded and (info.name == INT_CONTENT):
            logger.debug("[icnPubContent] receive interest: {}".format(info))
            i = info.chunk_num
            handle.send_data(INT_CONTENT, txChunk[i], i, expiry=expiry, cache_time=cacheTime)
            #logger.info ("[icnPubContent] send chunk num: {}".format(str(i)))

            if i == (segNum -1):
                i=i+1
                logger.debug("[icnPubContent] complete!")
                break

#Synchronization mode: (synchronize between Publisher and Consumer)
#old version. please do not use this function.
def syncIcnPubContent(handle, content, reqName, setting):

    segSize = setting["segSize"]
    cacheTime = setting["cacheTime"]
    expiry = setting["expiry"]
    TIMEOUT = setting["timeout"]

    content = content.encode('utf-8')

    #calculate required number of segments
    txSize = len(content)
    segNum = ((txSize -1) // segSize) + 1
    logger.info("[icnPubContent] required number of segments: {}".format(str(segNum)))

    txChunk = []

    for i in range(segNum):
        offset = i * segSize
        txChunk.insert(i, content[offset:offset + segSize])

    #define notify interest name
    #reqName[0]: prefix (ccn:)
    #reqName[1]: chain or proxy
    #reqName[2]: interest name
    INT_CONTROL = reqName[0] + "/" + reqName[1] + "/" + reqName[2]
    handle.register(INT_CONTROL)
    logger.debug("[icnPubContent] waiting for the notify packet: {}".format(INT_CONTROL))

    while True:

        #notify required segment number
        handle.send_data(INT_CONTROL, segNum, 0, expiry=expiry, cache_time=cacheTime)
        logger.debug("[icnPubContent] send content: {}".format(str(segNum)))

        #listen the interest packet for content
        INT_CONTENT = reqName[0] + "/" + reqName[2]
        handle.register(INT_CONTENT)
        logger.debug("[icnPubContent] wating for the interest packet: {}".format(INT_CONTENT))

        while True:
            info = handle.receive()
            if info.is_succeeded and (info.name == INT_CONTENT):
                logger.debug("[icnPubContent] receive interest: {}".format(info))
                for i in range(int(segNum)):
                    handle.send_data(INT_CONTENT, txChunk[i], i, expiry=expiry, cache_time=cacheTime)
                    #logger.info ("[icnPubContent] send chunk num: {}".format(str(i)))
                logger.debug("[icnPubContent] complete!")
                break
        break


#Synchronization mode: (synchronize between Publisher and Consumer)
def syncIcnPubContent_Old(handle, content, reqName, setting):

    segSize = setting["segSize"]
    cacheTime = setting["cacheTime"]
    expiry = setting["expiry"]
    TIMEOUT = setting["TIMEOUT"]

    content = content.encode('utf-8')

    #calculate required number of segments
    txSize = len(content)
    segNum = ((txSize -1) // segSize) + 1
    logger.info("[icnPubContent] required number of segments: {}".format(str(segNum)))

    txChunk = []

    for i in range(segNum):
        offset = i * segSize
        txChunk.insert(i, content[offset:offset + segSize])

    #define notify interest name
    #reqName[0]: prefix (ccn:)
    #reqName[1]: chain or proxy
    #reqName[2]: interest name
    INT_CONTROL = reqName[0] + "/" + reqName[1] + "/" + reqName[2]
    handle.register(INT_CONTROL)
    logger.debug("[icnPubContent] waiting for the notify packet: {}".format(INT_CONTROL))

    while True:

        #notify required segment number
        info = handle.receive()
        if info.is_succeeded and (info.name == INT_CONTROL) and (info.chunk_num == 0):
            handle.send_data(INT_CONTROL, segNum, 0, expiry=expiry, cache_time=cacheTime)
            logger.debug("[icnPubContent] send content: {}".format(str(segNum)))

            #listen the interest packet for content
            INT_CONTENT = reqName[0] + "/" + reqName[2]
            handle.register(INT_CONTENT)
            logger.debug("[icnPubContent] wating for the interest packet: {}".format(INT_CONTENT))

            while True:
                info = handle.receive()
                if info.is_succeeded and (info.name == INT_CONTENT):
                    logger.debug("[icnPubContent] receive interest: {}".format(info))
                    for i in range(int(segNum)):
                        handle.send_data(INT_CONTENT, txChunk[i], i, expiry=expiry, cache_time=cacheTime)
                        logger.debug("[icnPubContent] send chunk num: {}".format(str(i)))
                    logger.debug("[icnPubContent] complete!")
                    break
            break

#Asynchronization mode (Publisher just publishes content to the CS)
def asyncIcnPubContentV2(handle, content, reqName, setting):

    segSize = setting["segSize"]
    cacheTime = setting["cacheTime"]
    expiry = setting["expiry"]
    TIMEOUT = setting["timeout"]

    logger.debug("[icnPubContent] {} {} {}".format(segSize, cacheTime, TIMEOUT))

    content = content.encode('utf-8')

    #calculate required number of segments
    txSize = len(content)
    segNum = ((txSize -1) // segSize) + 1
    logger.info("[icnPubContent] required number of segments: {}".format(str(segNum)))

    txChunk = []

    for i in range(segNum):
        offset = i * segSize
        txChunk.insert(i, content[offset:offset + segSize])

    #define notify interest name
    #reqName[0]: prefix (ccn:)
    #reqName[1]: interest name
    INT_CONTENT = reqName[0] + "/" + reqName[1]
    logger.debug("[icnPubContent] interest message: {}".format(INT_CONTENT))
    handle.register(INT_CONTENT)

    handle.send_data(INT_CONTENT, txChunk[0], 0, end_chunk_num=segNum-1, expiry=expiry, cache_time=cacheTime)
    #handle.send_data(INT_CONTROL, segNum, 0)
    logger.debug("[icnPubContent] send content and last segment number: {}".format(str(segNum-1)))

    i=1

    while (i < segNum):
        handle.send_data(INT_CONTENT, txChunk[i], i, expiry=expiry, cache_time=cacheTime)
        #handle.send_data(INT_CONTENT, txChunk[i], i)
        #logger.info("[icnPubContent] send chunk num: {}".format(str(i)))
        i=i+1
    logger.debug("[icnPubContent] complete!")


#Asynchronization mode (Publisher just publishes content to the CS)
#old version. please do not use this function.
def asyncIcnPubContent(handle, content, reqName, setting):

    segSize = setting["segSize"]
    cacheTime = setting["cacheTime"]
    expiry = setting["expiry"]
    TIMEOUT = setting["timeout"]

    logger.debug("[icnPubContent] {} {} {}".format(segSize, cacheTime, TIMEOUT))

    content = content.encode('utf-8')

    #calculate required number of segments
    txSize = len(content)
    segNum = ((txSize -1) // segSize) + 1
    logger.info("[icnPubContent] required number of segments: {}".format(str(segNum)))

    txChunk = []

    for i in range(segNum):
        offset = i * segSize
        txChunk.insert(i, content[offset:offset + segSize])

    #define notify interest name
    #reqName[0]: prefix (ccn:)
    #reqName[1]: chain or proxy
    #reqName[2]: interest name
    INT_CONTROL = reqName[0] + "/" + reqName[1] + "/" + reqName[2]
    logger.debug("[icnPubContent] control message: {}".format(INT_CONTROL))
    handle.register(INT_CONTROL)

    handle.send_data(INT_CONTROL, segNum, 0, expiry=expiry, cache_time=cacheTime)
    #handle.send_data(INT_CONTROL, segNum, 0)
    logger.debug("[icnPubContent] send content: {}".format(str(segNum)))

    #listen the interest packet for content
    INT_CONTENT = reqName[0] + "/" + reqName[2]
    logger.debug("[icnPubContent] interest name: {}".format(INT_CONTENT))
    handle.register(INT_CONTENT)

    for i in range(int(segNum)):
        handle.send_data(INT_CONTENT, txChunk[i], i, expiry=expiry, cache_time=cacheTime)
        #handle.send_data(INT_CONTENT, txChunk[i], i)
        #logger.info("[icnPubContent] send chunk num: {}".format(str(i)))
    logger.debug("[icnPubContent] complete!")

#FIB update
def updateFib(fib):

    if fib["method"] == "add":
        logger.info("[fibUpdate] add fib {}".format(fib))
    if fib["method"] == "del":
        logger.info("[fibUpdate] delete fib {}".format(fib))

    CMD = ["sudo", "cefroute", fib["method"], fib["name"], PROTOCOL, fib["src"]]

    #call cefroute using subprocess
    result = subprocess.call(CMD)

    logger.info("[fibUpdate] fib update complete")

