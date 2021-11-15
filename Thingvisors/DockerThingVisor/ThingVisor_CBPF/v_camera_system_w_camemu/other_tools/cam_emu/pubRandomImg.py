import kafka
import time
import sys
import threading
import json
import os
import base64
import datetime
import random
from queue import Queue

from logging import basicConfig, getLogger, INFO

geometry = [35.7058879, 139.7060483]

SLEEP = 5
SIZE = 100

DATA_BROKER = ""
DATA_TOPIC = 'tokyo.01'

LOG_BROKER = ""
LOG_TOPIC = "tvf_log_out"

TIMEOUT = 10000

ImgDir = './test_seq_mini/'
NUM = 1

basicConfig(level=INFO)
logger = getLogger(__name__)

cbpf_data_model = {'@context': {
                        'type': 'StructuredValue',
                        'value': [
                          'http://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld',
                          'https://fed4iot.nz.comm.waseda.ac.jp/cbpfOntology/v1/cbpf-context.jsonld'
                          ]
                        },
                   'id': 'null',
                   'type': 'null',
                   'msg':
                       {#'id': {'type': '@id', 'value': cam_id},
                        #'type': {'type': '@id', 'value': 'camera'},
                        'location': {'type': 'GeoProperty', 'value': geometry},
                        'createdAt': {'type': 'Property', 'value': 'null'},
                        'source': {'type': 'Property', 'value': 'null'},
                        'dataProvider': {'type': 'Property', 'value': 'tokyo'},
                        'entityVesrion': {'type': 'Property', 'value': '1.0'},
                        'deviceModel': {'type': 'Relationship', 'value': 'WV-S1131'},
                        'description': {'type': 'Property', 'value': 'panasonic network camera'},
                        #'softwareVersion': {'type': 'Property', 'value': '1.0'},
                        'FileName': {'type': 'Property', 'value': 'null'},
                       }
                   }

def callReadImg():
  
    #num = random.randint(0, NUM-1)
    num = 0

    with open(ImgDir + str(num) + '.jpg', 'rb') as f:
        srcImg = f.read()
    
    binImg = base64.b64encode(srcImg).decode('utf-8')

    return binImg

def camProducer():

    print ("start camera thread")

    seq = 0

    #img_data = callReadImg()
    base_time = time.time()
    next_time = 0

    _cbpf_data_model = cbpf_data_model
    data_type = 'camera'
    data_id = 'urn:ngsi-ld:' + data_type + ':' + DATA_TOPIC.replace('.', ':')

    _cbpf_data_model['id'] = data_id
    _cbpf_data_model['type'] = data_type

    while True:

        img_data = callReadImg()
        cur_unixtime = time.time()
        timestamp = datetime.datetime.now(UTC)
        str_ts = timestamp.strftime('%Y-%m-%dT%H:%M:%S.%fZ')

        _cbpf_data_model['msg']['createdAt']['value'] = str_ts
        _cbpf_data_model['msg']['source']['value'] = img_data
        _cbpf_data_model['msg']['FileName']['value'] = str(cur_unixtime)+'.jpg'

        camQueue.put(_cbpf_data_model)

        #print ("cam: {} {}".format(str_ts, seq))
        seq = seq + 1

        next_time = ((base_time - time.time()) % SLEEP) or SLEEP

        time.sleep(next_time)

def pubKafkaProducer(data_topic, data_broker):

    print ("start kafka producer thread")

    prev_q_size = 0

    while True:
        if camQueue.empty():
            pass
        else:
            pub_data = camQueue.get()
            #timestamp = datetime.datetime.now(UTC)
            #str_ts = timestamp.strftime('%Y-%m-%dT%H:%M:%S.%fZ')    
            #seq = pub_data['seq']

            ### publish image data to data broker

            #pub_data.update({"id": DATA_TOPIC,
            #        "type": "camera",
            #        #"seq": seq,
            #        #"timestamp": str_ts,
            #        "kafka timestamp": str_ts,
            #        "gps": geometry,
            #        "queue size": prev_q_size
            #        #"content": {"value": img_data}
            #        })

            pub_data = json.dumps(pub_data)
 
            data_broker.send(DATA_TOPIC, pub_data.encode('utf-8'))
            camQueue.task_done()

            prev_q_size = camQueue.qsize()

            _pub_data = json.loads(pub_data)
            _pub_data['msg'].pop('source')

            print (json.dumps(_pub_data, indent=2))
            print ("publish")
            #print ("pub: {} {} {}".format(str_ts, seq, prev_q_size))

            #log_thread = threading.Thread(target=log_broker.send, args=([LOG_TOPIC, kafka_log.encode('utf-8')]))
            #log_thread.setDaemon(True)
            #log_thread.start()

            #print (json.dumps(json.loads(kafka_log),indent=2))


if __name__ == '__main__':

    ### connect kafka broker for data and logger
    data_broker = kafka.KafkaProducer(bootstrap_servers=DATA_BROKER,
            max_request_size=15728640,api_version_auto_timeout_ms=int(TIMEOUT))
    #log_broker = kafka.KafkaProducer(bootstrap_servers=LOG_BROKER,
    #        max_request_size=15728640,api_version_auto_timeout_ms=int(TIMEOUT))

    #data_broker = kafka.KafkaProducer(bootstrap_servers=DATA_BROKER,
    #        api_version_auto_timeout_ms=int(TIMEOUT))
    #log_broker = kafka.KafkaProducer(bootstrap_servers=LOG_BROKER,
    #        api_version_auto_timeout_ms=int(TIMEOUT))

    ### set timezone for influxDB
    UTC = datetime.timezone.utc
    
    camQueue = Queue(SIZE)

    cam_thread = threading.Thread(target=camProducer)
    #cam_thread = threading.Thread(target=sensorProducer)
    cam_thread.setDaemon(True)
    cam_thread.start()

    pubKafkaProducer(DATA_TOPIC, data_broker)

