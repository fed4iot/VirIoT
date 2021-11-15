'''
JSONファイルの定義
author：
datetime：2021.2.20
'''
# !/usr/bin/python
# -*- coding: utf-8 -*-
# import re
import json
import datetime
import config


json_data = '''{
                "dev_id": "TX2",
                "cam_no": "PANA_1",
                "d_time": [],
                "gps_info": {
                    "type": "point",
                    "crs": {
                        "type": "name",
                        "properties": {
                            "name": "urn:ogc:def:crs:0GC:1.3:CRS84"
                            }
                        },
                    "coordinates": [0.0, 0.0]
                    },
                "img_name": []
                }'''

json_data1 = '''{
                "dev_id": "jetsonTX2",
                "cam_no": "PANA_1",
                "d_time": [],
                "gps_info": {
                    "coordinates": [0.0, 0.0]
                },
                "img_name": []
                }'''

JSON_FILE_PATH = config.json_file_dir + config.json_name

UTC = datetime.timezone.utc

# DATE_KEY = re.compile(r'date_time$')
# IMG_URI = re.compile(r'IMG_URI$')
# COORDINATES = re.compile(r'coordinates$')


def _json_parser(img_name):

    #json_dict = json.loads(json_data)

    #json_dict['d_time'] = datetime.now().strftime('%Y%m%d%H%M%S')
    #json_dict['gps_info']['coordinates'] = [32.7899, 130.7425]
    #json_dict['img_name'] = img_name

    json_dict = config.cbpf_data_model

    print (json_dict)
    print (type(json_dict))

    timestamp = datetime.datetime.now(UTC).strftime('%Y-%m-%dT%H:%M:%SZ')
    json_dict['msg']['createdAt']['value'] = timestamp
    json_dict['msg']['FileName']['value'] = img_name

    #json_dict['HumanDetector']['createdAt']['value'] = timestamp
    #json_dict['HumanDetector']['DetectHuman']['value'] = True

    json_dumps = json.dumps(json_dict)

    return json_dumps


def get_json_data(img_name):
    # img_uri = config.temp_image_dir + img_name
    img_uri = img_name

    print("JSON_FILE_PATH", JSON_FILE_PATH)
    #with open(JSON_FILE_PATH, 'w') as file_obj:
    json_dumps = _json_parser(img_uri)

    return json_dumps


def save_json_file(img_name):
    json_dumps = get_json_data(img_name)
    print("json.dumps", json_dumps)

    with open(JSON_FILE_PATH, 'w') as file_obj:
        json.dump(json_dumps, file_obj)


def get_json_file():
    return JSON_FILE_PATH
