import os
import uuid
from PIL import Image, ImageDraw
from time import sleep
from azure.cognitiveservices.vision.face import FaceClient
from msrest.authentication import CognitiveServicesCredentials
from azure.cognitiveservices.vision.face.models import TrainingStatusType, Person
#from face_recognition_azure.create_face_client import face_client

import json
import base64
import time
import datetime
from common import common

# This key will serve all examples in this document.
KEY = ""

# This endpoint will be used in all examples in this quickstart.
ENDPOINT = ""

# Create an authenticated FaceClient.
face_client = FaceClient(ENDPOINT, CognitiveServicesCredentials(KEY))

#img_path = "test.jpg"
temp = "temp.jpg"
UTC = datetime.timezone.utc

#with open(img_path, 'rb') as f:
#    img = f.read()

#_img_64 = base64.b64encode(img).decode('utf-8')

location_name = 'tokyo'
service_name = 'humandetector'
cbpf_data_model = {'@context': {
                        'type': 'StructuredValue',
                        'value': [
                          'http://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld',
                          'https://fed4iot.nz.comm.waseda.ac.jp/cbpfOntology/v1/cbpf-context.jsonld'
                          ]
                        },
                    'id': 'urn:ngsi-ld:humandetector:' + location_name + ':01',
                    'type': 'humandetector',
                    'msg': {'location': {'type': 'GeoProperty', 'value': 'null'},
                            'createdAt': {'type': 'Property', 'value': 'null'},
                            #'soruce': {'type': 'Property', 'value': pana_cam_url},
                            'dataProvider': {'type': 'Property', 'value': 'null'},
                            'entityVesrion': {'type': 'Property', 'value': '1.0'},
                            'description': {'type': 'Property', 'value': 'virtual human detector'},
                            'softwareVersion': {'type': 'Property', 'value': '1.0'},
                            'NumberOfHuman': {'type': 'Property', 'value': 'null'},
                            'DetectHuman': {'type': 'Property', 'value': 'null'},
                           }
                    }

def callService(interest, rxData, ARGS):

    src_name = common.getContentName(interest)
    _src_name = src_name.replace('.', ':')
    _img_64 = rxData['msg']['source']['value']
    location = rxData['msg']['location']
    dataProvider = rxData['msg']['dataProvider']

    srcImg = base64.b64decode(_img_64.encode('utf-8'))
    with open(temp, 'wb') as f:
        f.write(srcImg)

    f_img = open(temp, 'rb')
    result = face_detect(f_img)
    timestamp = datetime.datetime.now(UTC).strftime('%Y-%m-%dT%H:%M:%S.%fZ')

    _cbpf_data_model = cbpf_data_model

    _cbpf_data_model['id'] = 'urn:ngsi-ld:' + service_name + ':' + _src_name
    _cbpf_data_model['msg']['location'] = location
    _cbpf_data_model['msg']['createdAt']['value'] = timestamp

    if result is not None:
        _cbpf_data_model['msg']['NumberOfHuman']['value'] = len(result)
        _cbpf_data_model['msg']['DetectHuman']['value'] = result
    else:
        pass

    _cbpf_data_model['msg']['dataProvider'] = dataProvider

    print (json.dumps(_cbpf_data_model, indent=2))
    
    return _cbpf_data_model

def face_detect(image):
    '''
    :param image_path: 探したい人の画像の保存パス　image/find_image/
    :param image: カメラのフィルムイメージ
    :return: 顔識別結果、イメージファイルの名前
    '''
    # Each detected face gets assigned a new ID

    """
    if image_path is None and image is None:
        # raise Exception('No face detected from image.')
        return None, None
    if image is None:
        multi_face_image_path = image_path
        multi_image_name = os.path.basename(multi_face_image_path)
        detect_image = open(multi_face_image_path, 'rb')
        #detect_show_image = Image.open(multi_face_image_path, 'r')
    """

    detect_image = image
    # We use detection model 3 to get better performance.

    try:
        detected_faces = ''
        detected_faces = face_client.face.detect_with_stream(image=detect_image, detection_model='detection_03')
    except Exception as e:
        print(e)
        sleep(5)

    # print('Detected face IDs from', multi_image_name, ':')
    if not detected_faces:
        # raise Exception('No face detected from image {}.'.format(multi_image_name))
        return None
    else:

        detected_face_IDs = list(map(lambda x: x.face_id, detected_faces))
        #for d_face in detected_faces:
        #    print(d_face.face_id)
        #    continue
        #print_image_draw_rect(detect_show_image, multi_detected_faces)

        print (detected_face_IDs)

    return detected_face_IDs

if __name__ == "__main__":
    
    main()
