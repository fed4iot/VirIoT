import json
import base64
import socket
import sys
import uuid
from logging import getLogger

logger = getLogger(__name__)

def getContentName(interest):

    listName = interest.split("/")
    numName = len(listName)

    logger.debug("[getContentName] {}".format(listName))

    #last name is content name
    return listName[numName-1]

def callService(content, interest, host, service, revSize):

    logger.debug("[callService] start calling service function")

    if service['input'] == "only content":
        if content != b'':
            contentName = getContentName(interest)
            temp = json.loads(content)
            temp = temp[contentName]['content']['value']
            inputData = base64.b64decode(temp.encode('utf-8'))

    else:
        if content != b'':
            inputData = content.encode()

    port = int(service['port'])

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:

        s.connect((host, port))

        #sending input data
        if content != b'':
            s.sendall(inputData)
            s.shutdown(1)
        ########

        #receiving data from service function
        revData = b''
        data = s.recv(revSize)
        revData += data

        if sys.getsizeof(data) > revSize:

            while True:
                data = s.recv(revSize)
                #revData += data
                #print(sys.getsizeof(data))
                #if sys.getsizeof(data) < revSize:
                #    revData += data
                #    break
                if not data:
                    break 
                revData += data

        result = revData.decode()
        #########

        logger.debug("[callService] complete")

        return result


def concatData(rawData, procData, funcName):

    logger.debug("[concatData] data serialization")

    BODY = []

    if funcName == "yolo" or funcName == "yologpu" or funcName == "yolotiny":

        YOLO = []
        if (procData != "null"):

            temp = procData.split("_")
            numDetect = len(temp)

            for i in range(numDetect-1):

                temp2 = temp[i].split(",")

                left = temp2[2]
                right = temp2[3]
                top = temp2[4]
                bottom = temp2[5]
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

        procData = YOLO

    if type(procData) is str:
        procData = json.loads(procData)

    if type(rawData) is str:
        rawData = json.loads(rawData)

    BODY = rawData
    BODY.update({funcName: procData})

    BODY = json.dumps(BODY)

    #logger.info("[concatData] data {}".format(BODY))

    logger.debug("[concatData] complete!")

    return BODY
