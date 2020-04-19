
import paho.mqtt.client as mqtt
import json
import time


class OM2MPubSub:
    def __init__(self, broker_ip, broker_port):
        self.mqtt_client = mqtt.Client()
        self.mqtt_client.connect(broker_ip, broker_port)
        self.mqtt_client.loop_start()

    # Publish content instance
    def create_cin_mqtt(self, container_uri, origin, value, cse, ae):
        topic = "/oneM2M/req/" + ae + "/" + cse + "/json"
        rqp = {"m2m:rqp":
               {"fr": origin,
                "to": container_uri,
                "op": 1,
                "rqi": time.time(),
                "ty": 4,
                "pc":
                {"m2m:cin":
                 {"con": value}
                 }
                }
               }
        self.mqtt_client.publish(topic = topic, payload =  json.dumps(rqp), qos = 1)

        return "Content instance sent"
        
