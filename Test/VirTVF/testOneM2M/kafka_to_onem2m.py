import requests
import json
import random
import time
import kafka

BROKER = "133.9.250.223"
PORT = "8000"

KAFKA = "133.9.250.211:9092"
TOPIC = "camera"

RN = ["waseda", "netcam"]

SLEEP = 10

def createAppResource(baseURI, headers, RN):

    data = { "m2m:ae": {
                "rn": RN[0],
                "api": "placeholder",
                "rr": "TRUE"
                }
            }

    response = requests.post(baseURI, headers=headers, data=json.dumps(data))

def createContainerResource(baseURI, headers, RN):

    data = { "m2m:cnt": {
                "rn": RN[1]
                }
            }

    response = requests.post(baseURI+RN[0]+"/", headers=headers, data=json.dumps(data))

if __name__ == '__main__':

    headers  = {
             'Content-Type': 'application/vnd.onem2m-res+json',
             }

    baseURI = 'http://'+BROKER+":"+PORT+"/onem2m/"

    createAppResource(baseURI, headers, RN)
    createContainerResource(baseURI, headers, RN)


    print ("Subscribe kafka broker with topic: {}".format(TOPIC))
    consumer = kafka.KafkaConsumer(bootstrap_servers=KAFKA, fetch_max_bytes=15728640)
    consumer.subscribe([TOPIC])



    for message in consumer:

        print ("Receive data from kafka broker")
        rxData = message.value.decode()
        body = rxData

        #body = {"id": "person",
        #        "score": random.randint(0,100)
        #        }

        #body = "test"


        data = {"m2m:cin": {
                    "con": body,
                    "cnf":"text/plain:0"
                     }
                }

        endPoint = baseURI + RN[0] + "/" + RN[1] + "/"

        print ("publish to onem2m broker")
        response = requests.post(endPoint, headers=headers, data=json.dumps(data))
        #response = requests.post(endPoint, headers=headers, data=data)
        print (data)
        print (response)

        #time.sleep(SLEEP)
