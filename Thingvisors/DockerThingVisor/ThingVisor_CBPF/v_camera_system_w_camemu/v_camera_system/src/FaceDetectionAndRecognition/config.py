'''
システム設定
author：
datetime：2021.2.20
'''
# !/usr/bin/python
# -*- coding: utf-8 -*-
import os
from datetime import date, datetime

current_file = __file__

current_date = date.today().strftime('%Y%m%d')
current_date_time = datetime.now().strftime('%Y%m%d%H%M%S')

# get root path
root_path = os.path.abspath(os.path.join(current_file, os.pardir))

# setting write log file path
log_path = os.path.abspath(os.path.join(root_path, 'log')) + '/'

# setting webcam
webcam_id = 0

# setting pana camera
pana_cam_no = "pana_1/"

pana_cam_url = 'http://192.168.11.160:8080/nphMotionJpeg?Resolution=640x360&Quality=Standar'

#location_name = 'tokyo'
#location_name = 'murcia'
#location_name = 'grasse'
#location_name = 'kumamoto'
location_name = 'hakusan'

data_provider = location_name

# setting GPS
#cam_long = 130.696874
#cam_lat = 32.83127
cam_long = 136.590063
cam_lat = 36.545158

# data model

#cam_id = 'urn:ngsi-ld:' + location_name + ':camera:01'
#service_id = 'urn:ngsi-ld:' + location_name + ':FaceFeatureDetector:01'

cbpf_data_model = {'@context': {
                        'type': 'StructuredValue',
                        'value': [
                          'http://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld',
                          'https://fed4iot.nz.comm.waseda.ac.jp/cbpfOntology/v1/cbpf-context.jsonld'
                          ]
                        },
                   'id': 'urn:ngsi-ld:cbpf:' + location_name + ':01',
                   'type': 'cbpf',
                   'msg': 
                       {#'id': {'type': '@id', 'value': cam_id},
                        #'type': {'type': '@id', 'value': 'camera'},
                        'location': {'type': 'GeoProperty', 'value': [cam_lat, cam_long]},
                        'createdAt': {'type': 'Property', 'value': 'null'},
                        #'soruce': {'type': 'Property', 'value': pana_cam_url},
                        'dataProvider': {'type': 'Property', 'value': data_provider},
                        'entityVesrion': {'type': 'Property', 'value': '1.0'},
                        'deviceModel': {'type': 'Relationship', 'value': 'WV-S1131'},
                        'description': {'type': 'Property', 'value': 'panasonic network camera'},
                        #'softwareVersion': {'type': 'Property', 'value': '1.0'},
                        'FileName': {'type': 'Property', 'value': 'null'},
                       }
                   }
                   #'HumanDetector': 
                   #    {'id': {'type': '@id', 'value': service_id},
                   #     'type': {'type': '@id', 'value': 'human detector'},
                   #     'location': {'type': 'GeoProperty', 'value': [cam_lat, cam_long]},
                   #     'createdAt': {'type': 'Property', 'value': 'null'},
                   #     #'soruce': {'type': 'Property', 'value': pana_cam_url},
                   #     'dataProvider': {'type': 'Property', 'value': 'null'},
                   #     'entityVesrion': {'type': 'Property', 'value': '1.0'},
                   #     'description': {'type': 'Property', 'value': 'virtual person finder'},
                   #     'softwareVersion': {'type': 'Property', 'value': '1.0'},
                   #     'DetectHuman': {'type': 'Property', 'value': False},
                   #    }
                   #},
                   #'FaceFeatureDetector':
                   #    {'id': {'type': '@id', 'value': service_id},
                   #     'type': {'type': '@id', 'value': 'human detector'},
                   #     'location': {'type': 'GeoProperty', 'value': [cam_lat, cam_long]},
                   #     'createdAt': {'type': 'Property', 'value': 'null'},
                   #     #'soruce': {'type': 'Property', 'value': pana_cam_url},
                   #     'dataProvider': {'type': 'Property', 'value': 'null'},
                   #     'entityVesrion': {'type': 'Property', 'value': '1.0'},
                   #     'description': {'type': 'Property', 'value': 'virtual person finder'},
                   #     'softwareVersion': {'type': 'Property', 'value': '1.0'},
                   #    }
                   #}


# setting image file dir
img_file_dir = os.path.abspath(os.path.join(root_path, 'image')) + '/'

# setting image file dir
json_file_dir = os.path.abspath(os.path.join(root_path, 'json-data')) + '/'

json_name = 'information.json'
send_json_file = 'information_send.json'

# 探したい人の顔写真保存場所
find_img_dir = os.path.abspath(os.path.join(root_path, 'image', 'find_image')) + '/'
# カメラからキャプチャーを取った写真の一時保存場所
temp_image_dir = os.path.abspath(os.path.join(root_path, 'image', 'temp_image')) + '/'
# キャッシュファイル場所
cache_dir = os.path.abspath(os.path.join(root_path, 'cache')) + '/'

# setting casade file
# multiple cascades: https://github.com/Itseez/opencv/tree/master/data/haarcascades
cascade_frontal_face_alt = os.path.abspath(os.path.join(root_path,
                                                        'haarcascades/haarcascade_frontalface_alt.xml'))
cascade_frontal_cat_face = os.path.abspath(os.path.join(root_path, 'haarcascades/haarcascade_frontalcatface.xml'))

cascade_frontal_face_default = os.path.abspath(os.path.join(root_path,
                                                            'haarcascades/haarcascade_frontalface_default.xml'))

# mqtt parameter
# Host = "169.56.56.97"
Host = "localhost"
# Host = "192.168.0.105"

Port = 1883
Keepalive = 60
MovinWaitSec = 0.01

# Topic
# topic = 'topic'
topic = 'Pana/pana_cam'

# windows PC test
# T_Face = "D:/web_camera_c/facial_recognition/"
T_Face = "/web_camera_c/facial_recognition/"
T_Move = "web_camera_c/moving_object/"

FACE_PANA = 'FACE_PANA'
MOVE_PANA = 'MOVE_PANA'

# Srctopic = 'web_camera/cam_1'
Srctopic = 'Pana/+'
Pana_topic = 'Pana/'
Color = (255, 255, 255)
Timestamp = "20000101"
Command = "mosquitto_pub -h "
Topicopt = " -t "
Fileopt = " -f "
# Fileext = ".jpg"
Fileext = ".json"
Facerec = "_facecut_"
Dummyfile = "Dummyfile"

Filename_Moving = "_moving_objct"
Filename_Image = "_image"
# mqtt parameter

MAX_JSON_CONTENT_LENGTH = 1048576
