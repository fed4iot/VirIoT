#import cefpyco
import sys
import time
import threading
import json
import os
#import netifaces as ni
from logging import basicConfig, getLogger, DEBUG, INFO

#import from tvFactoryLibrary
from common import common
#from protocol import icnCefore
#from protocol import kafka
#####

SETTING = "./config/nodeSetting.json"

def callObjectCounter(interest, rxData, targetService, targetTag):

    content = json.loads(rxData)
    data = content[targetService]
    count = 0

    for i in range(len(data)):
        if (data[i]['tagName'] == targetTag):
            count = count + 1

    serviceName = common.analyzeInterest(interest)[1]

    #extract data without raw image
    contentName = common.getContentName(interest)
    content[contentName].pop('content')
    
    #data model
    body = {'id': serviceName + ':' + targetService + ':' + targetTag,
            'type': 'service function',
            'content': {'type': 'Property', 'value': count}
           }

    content.update({serviceName: body})
    return content
