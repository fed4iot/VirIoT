import argparse, argcomplete
import sys
import traceback
import time
import os
import socket
import json
from threading import Thread
import requests
import random
import string

UNIT = 10**3

def random_char(y):
       return ''.join(random.choice(string.ascii_letters) for x in range(y))

if __name__ == '__main__':


    message = {
        "timestamp": 313,
        "sqn":0
    }


    try:
        parser = argparse.ArgumentParser()
        parser.add_argument('-b', action='store', dest='brokerUrl',
                            help='brokerUrl (default: http://172.17.0.3:1026/v2/entities)', default='http://172.17.0.3:1026/v2/entities')
        parser.add_argument('-i', action='store', dest='entityIdentifier', 
                            help='entityIdentifier (default: testIdentifier) ', default='testIdentifier')
        parser.add_argument('-t', action='store', dest='entityType', 
                            help='entityType (default: testMessage) ', default='testMessage')
        parser.add_argument('-r', action='store', dest='rate', 
                            help='Message rate msg/s (default: 1 msg/s)', default='1')
        parser.add_argument('-s', action='store', dest='payloadsize', 
                            help='Payloadsize in characters (default: 10 chars)', default='10')
        parser.add_argument('-v', action='store_true', dest='verbose', 
                            help='Print verbose output')
        argcomplete.autocomplete(parser)
        args = parser.parse_args()
    except Exception:
        traceback.print_exc()

    time.sleep(2)
    cnt = 1
    while True:
        try:
            time.sleep(1.0/float(args.rate))

            # Test with POST
            message['timestamp'] = int(round(time.time()*(UNIT)))
            message['sqn'] = cnt
            message['payloadstring'] = random_char(int(args.payloadsize))

            entity_type = args.entityType
            entity_id = args.entityIdentifier
            attribute = {
                "type": "StructuredValue",
                "value": message
            }
            ngsiv2container = {
                "id": "urn:ngsi-ld:"+entity_id,
                "type": entity_type,
                "msg": attribute
            }
            headers = {
                'Content-Type': "application/json",
                'Accept': "application/json"
            }
            # overwrite existing entity with same id
            params = {'options': 'upsert'}
            data = json.dumps(ngsiv2container)
            r = requests.post(args.brokerUrl, data=data, headers=headers, params=params)
            cnt += 1
            if args.verbose:
                print("Message sent: "+data)
        except Exception as err:
            print("KeyboardInterrupt", err)
            time.sleep(1)
            os._exit(1)

