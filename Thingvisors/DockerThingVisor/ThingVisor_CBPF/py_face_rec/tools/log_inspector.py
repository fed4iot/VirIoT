import cefpyco
import sys
import time
import threading
import json
import os
#import netifaces as ni
from logging import basicConfig, getLogger, DEBUG, INFO

#import from tvFactoryLibrary
#from common import common
#from protocol import icnCefore
from protocol import kafka
#####

#BROKER = "192.168.11.101:9092"
BROKER = "133.9.250.209:9092"
#BROKER = "133.9.250.211:9092"
#BROKER = "133.9.250.228:9092"
TOPIC_SUB = "tvf_log_out"

if __name__ == '__main__':

    #TOPIC_SUB = sys.argv[1]

    kafkaBroker = kafka.kafkaConnect(BROKER)

    print ("[main] kafka mode")

    consumer = kafka.kafkaSubContent(BROKER, TOPIC_SUB)
    print ("[main] subscribe topic {}".format(TOPIC_SUB))

    for message in consumer:

        rxData = message.value.decode()
        rxData = json.loads(rxData)
        #print (json.dumps(rxData,indent=2))

        content = rxData['content']
        metric_log = content.pop('metric')

        print (content['service id'], content['delay']['get time'], content['delay']['proc time'], content['delay']['pub time'])

        #print (json.dumps(content,indent=2))

        kafka_metrics = consumer.metrics()

        key_lists = list(kafka_metrics.keys())
        value_lists = list(kafka_metrics.values())

        temp = {}
        if (len(key_lists) == len(value_lists)):
            for i in range(len(key_lists)):
                #print (key_lists[i])
                if "." in key_lists[i]:
                    key_lists[i] = key_lists[i].replace('.', '%')
                else:
                    pass
        else:
            pass

        temp = dict(zip(key_lists, value_lists))

        #print (json.dumps(temp,indent=2))
