import kafka
import json
import csv
import os
import datetime
import time
import threading
import subprocess
import geohash
import base64
from influxdb import InfluxDBClient

setting_path = './setting.json'
with open(setting_path) as f:
    setting = json.load(f)

kafka_ip = setting['control broker ip']
kafka_port = setting['control broker port']
control_topic_k8s=setting['control topic']
influxdb_ip = setting['influxdb ip']
influxdb_port = int(setting['influxdb port'])
influxdb_user = setting['influxdb user']
influxdb_pass = setting['influxdb pass']
influxdb_database = setting['influxdb database']

log_path = './logs/'
log_ext = '.csv'

request_img = './test_request.jpg'

with open(request_img, 'rb') as f:
    srcImg = f.read()
    b64Img = base64.b64encode(srcImg).decode('utf-8')

kafka_key = "producer-topic-metrics"

def main():

    ### Connect InfluxDB
    influx_client = InfluxDBClient(influxdb_ip, influxdb_port, influxdb_user, influxdb_pass, influxdb_database)
    influx_client.create_database(influxdb_database)
    ###

    ### check output directory for log
    if os.path.exists(log_path) == False:
        os.makedirs(log_path)

    timestamp = datetime.datetime.now()
    log_name = timestamp.strftime('%Y-%m-%dT%H:%M:%SZ')

    print ('start cbpf app exporter') 

    app_exporter(log_name, influx_client)

def csvWriter(file_path, data):

     with open(file_path, 'a') as f:
        writer = csv.writer(f)
        writer.writerow(data)


def cbpf_app(log_data,log_name, influx_client):

    data_id = log_data['dataProvider']['value']
    data_type = 'cbpf'
    timestamp = log_data['createdAt']['value']
    location = log_data['location']['value']
    geohash_value = geohash.encode(location[0], location[1])
    flag = 1

    nodes_log_path = log_path + 'nodes_' + log_name + log_ext

    mem_name = "cbpf_app_dashboard"
    mem_name2 = "cbpf_app_img"

    data_to_db = [{"measurement": mem_name,
                     "tags": {"id": data_id,
                              "type": "byte-rate",
                              "geohash": geohash_value},
                     "time": timestamp,
                     "fields": {"value": flag}
                  },
                   {"measurement": mem_name2,
                     "tags": {"id": data_id,
                              "type": "image"},
                     "time": timestamp,
                     "fields": {"name": "img",
                                "type": "string",
                                "value": b64Img}
                  }]

    influx_client.write_points(data_to_db)

    #csvWriter(nodes_log_path, result)

    print ("store to db")

def app_exporter(log_name, influx_client):

    CONT_KAFKA = kafka_ip + ":" + kafka_port
    consumer = kafka.KafkaConsumer(bootstrap_servers=CONT_KAFKA,fetch_max_bytes=15728940)
    consumer.subscribe([control_topic_k8s])

    for message in consumer:
        data = message.value.decode()
        data = json.loads(data)

        print (json.dumps(data, indent=2))

        cbpf_app(data, log_name, influx_client)

if __name__ == '__main__':

    main()
