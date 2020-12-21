#rn : resource name
#ri : resource identifier
#origin: originator identifier (AE ri usually)
#CSEurl: url of the CSE server
#rr: true/false if should be reachable (request reachability)
#poa: point of access, url where to be contacted (rr=true)
#nu: norification uri (url or AE ri if AE containd poa)
#container_rn: resource name of the container, e.g. 
#ae_rn: resouce name of the AE
#sub_rn: sub resource name
#mni: max num instances

import argparse, argcomplete
import sys,getopt
import F4Im2m
import json
import time
import traceback
import random
import os
import string
import F4Im2m


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
                            help='brokerUrl (default: http://172.17.0.3:30880)', default='http://172.17.0.3:30880')
        parser.add_argument('-n', action='store', dest='vThingName', 
                            help='vThingName (default: testVThing) ', default='testVThing')
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

    status,ae=F4Im2m.ae_create(args.vThingName,args.vThingName,"xxx","false","",[],args.brokerUrl)
    print(status)

    if status==409:
        print("Deleting")
        status,ae=F4Im2m.ae_delete("Mobius/"+args.vThingName,args.vThingName,args.brokerUrl)
        print(status)
        print("Creating")
        status,ae=F4Im2m.ae_create(args.vThingName,args.vThingName,"xxx","false","",[],args.brokerUrl)
        print(status)

    # relay TV creates a container with same name of AE
    status,cnt=F4Im2m.container_create(args.vThingName,ae['ri'],ae['uri'],200,[args.entityType],args.brokerUrl)
    print(status)
    
    status,sub_cnt=F4Im2m.container_create("msg",ae['ri'],cnt['uri'],200,[],args.brokerUrl)
    print(status)

    data = json.dumps(message)

    print(sub_cnt['uri'])
    status,cin=F4Im2m.create_cin(sub_cnt['uri'],ae['ri'],data,args.brokerUrl)
    print(status)


    time.sleep(2)
    cnt = 1
    while True:
        try:
            time.sleep(1.0/float(args.rate))

            # Test with POST
            message['timestamp'] = int(round(time.time()*(UNIT)))
            message['sqn'] = cnt
            message['payloadstring'] = random_char(int(args.payloadsize))

            value = {}
            value['value']=message
            data = json.dumps(value)
            data = json.dumps(message)

            print("create_cin")
            status,cin=F4Im2m.create_cin(sub_cnt['uri'],ae['ri'],data,args.brokerUrl)
            print(status)

            print("get_cin_latest")
            status,cin=F4Im2m.get_cin_latest(sub_cnt['uri'],ae['ri'],args.brokerUrl)
            print(status)

            cnt += 1

            if args.verbose:
                print("Message sent: "+data)
        except Exception as err:
            print("KeyboardInterrupt", err)
            time.sleep(1)
            os._exit(1)
