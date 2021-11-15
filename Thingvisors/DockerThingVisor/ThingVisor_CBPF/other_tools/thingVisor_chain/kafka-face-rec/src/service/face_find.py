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

img_path = "./service/request.jpg"
#temp = "temp.jpg"
UTC = datetime.timezone.utc

#with open(img_path, 'rb') as f:
#    img = f.read()

#_img_64 = base64.b64encode(img).decode('utf-8')

location_name = 'tokyo'
service_name = 'findface'
cbpf_data_model = {'@context': {
                        'type': 'StructuredValue',
                        'value': [
                          'http://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld',
                          'https://fed4iot.nz.comm.waseda.ac.jp/cbpfOntology/v1/cbpf-context.jsonld'
                          ]
                        },
                    'id': 'null',
                    'type': service_name,
                    'msg': {'location': {'type': 'GeoProperty', 'value': 'null'},
                            'createdAt': {'type': 'Property', 'value': 'null'},
                            #'source': {'type': 'Property', 'value': 'null'},
                            'dataProvider': {'type': 'Property', 'value': 'null'},
                            'entityVesrion': {'type': 'Property', 'value': '1.0'},
                            'description': {'type': 'Property', 'value': 'find face service'},
                            'softwareVersion': {'type': 'Property', 'value': '1.0'},
                            'faceFound': {'type': 'Property', 'value': 'null'}
                            #'FaceLandMarkInfo': {'type': 'Property', 'value': 'null'},
                            #'KeyInfo': {'type': 'Property', 'value': 'null'},
                           }
                    }

def callService(interest, rxData, ARGS):

    src_name = common.getContentName(interest)
    _src_name = src_name.replace('.', ':')
    detect_human_ids = rxData['msg']['DetectHuman']['value']
    location = rxData['msg']['location']
    dataProvider = rxData['msg']['dataProvider']

    result = False
    if (detect_human_ids != 'null' and os.path.exists(img_path) is True):
        face_id = single_face_detect(img_path)
        result = find_similar_face(face_id, detect_human_ids)
    else:
        pass

    timestamp = datetime.datetime.now(UTC).strftime('%Y-%m-%dT%H:%M:%S.%fZ')

    _cbpf_data_model = cbpf_data_model

    _cbpf_data_model['id'] = 'urn:ngsi-ld:' + service_name + ':' + _src_name
    _cbpf_data_model['msg']['location'] = location
    _cbpf_data_model['msg']['createdAt']['value'] = timestamp
    _cbpf_data_model['msg']['dataProvider'] = dataProvider

    _cbpf_data_model['msg']['faceFound']['value'] = result
    #_cbpf_data_model['msg']['FaceLandMarkInfo']['value'] = face_land_mark
    #_cbpf_data_model['msg']['KeyInfo']['value'] = 'sha-256'

    print (json.dumps(_cbpf_data_model, indent=2))
    
    return _cbpf_data_model


def single_face_detect(image_path):
    '''

    :param image_path:
    :return:
    '''

    # Detect a face in an image that contains a single face
    single_face_image_path = image_path
    # single_image_name = os.path.basename(single_face_image_path)
    # print('single_face_image_path: ', single_face_image_path)
    # We use detection model 3 to get better performance.
    find_image = open(single_face_image_path, 'rb')
    try:
        detected_faces = ''
        detected_faces = face_client.face.detect_with_stream(image=find_image, detection_model='detection_03')
    except Exception as e:
        print(e)
        sleep(5)

    if not detected_faces:
        # raise Exception('No face detected from image {}'.format(single_image_name))
        return None

    # Display the detected face ID in the first single-face image.
    # Face IDs are used for comparison to faces (their IDs) detected in other images.
    # print('Detected face ID from', single_image_name, ':')
    for face in detected_faces:
        # print(face.face_id)
        continue
    # Save this ID for use in Find Similar
    first_image_face_ID = detected_faces[0].face_id

    return first_image_face_ID


def find_similar_face(find_face_id, detected_human_ids):
    '''
    Find a similar face
    This example uses detected faces in a group photo to find a similar face using a single-faced image as query.
    :param find_face_id:
    :param detected_faces:
    :param multi_image_name:
    :return:
    '''

    # Search through faces detected in group image for the single face from first image.
    # First, create a list of the face IDs found in the second image.
    #second_image_face_IDs = list(map(lambda x: x.face_id, detected_faces))
    # Next, find similar face IDs like the one detected in the first image.
    similar_faces = face_client.face.find_similar(face_id=find_face_id, face_ids=detected_human_ids)
    face_land_mark = []
    if not similar_faces:
        print('No similar faces found')
        return False
    # Print the details of the similar faces detected
    else:
        # print('Similar faces found in', multi_image_name)
        #for face in similar_faces:
        #    first_image_face_ID = face.face_id
            # The similar face IDs of the single face image and the group image do not need to match,
            # they are only used for identification purposes in each image.
            # The similar faces are matched using the Cognitive Services algorithm in find_similar().
            #face_info = next(x for x in detected_faces if x.face_id == first_image_face_ID)
            #if face_info:
            #    face_result = {"face id": first_image_face_ID, 
            #                   "face rectangle": 
            #                    {"left": str(face_info.face_rectangle.left),
            #                     "top": str(face_info.face_rectangle.top),
            #                     "width": str(face_info.face_rectangle.width),
            #                     "height": str(face_info.face_rectangle.height)
            #                    }
            #                   }
            #    face_land_make.append(face_result)
        return True


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
