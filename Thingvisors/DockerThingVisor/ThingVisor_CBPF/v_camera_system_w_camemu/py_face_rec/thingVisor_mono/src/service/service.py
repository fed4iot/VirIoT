import os
import uuid
from time import sleep
import face_recognition

import json
import base64
import time
import datetime
from common import common

img_path = "./service/request.jpg"
temp = "temp.jpg"
UTC = datetime.timezone.utc

detect_model = "cnn"
#detect_model = "hog"

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
                    'id': 'urn:ngsi-ld:' + service_name + ':' + location_name + ':01',
                    'type': 'humandetector',
                    'msg': {'location': {'type': 'GeoProperty', 'value': 'null'},
                            'createdAt': {'type': 'Property', 'value': 'null'},
                            'source': {'type': 'Property', 'value': 'null'},
                            'dataProvider': {'type': 'Property', 'value': 'null'},
                            'entityVesrion': {'type': 'Property', 'value': '1.0'},
                            'description': {'type': 'Property', 'value': 'face finder'},
                            'softwareVersion': {'type': 'Property', 'value': '1.0'},
                            'NumberOfHuman': {'type': 'Property', 'value': 'null'},
                            'DetectHuman': {'type': 'Property', 'value': 'null'},
                            'faceFound': {'type': 'Property', 'value': 'null'}
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

    timestamp = datetime.datetime.now(UTC).strftime('%Y-%m-%dT%H:%M:%S.%fZ')

    _cbpf_data_model = cbpf_data_model

    _cbpf_data_model['id'] = 'urn:ngsi-ld:' + service_name + ':' + _src_name
    _cbpf_data_model['msg']['location'] = location
    _cbpf_data_model['msg']['createdAt']['value'] = timestamp
    _cbpf_data_model['msg']['dataProvider'] = dataProvider


    if _img_64 != "null":
        src_img = face_recognition.load_image_file(temp)
        face_result = face_recognition.face_locations(src_img, model=detect_model)

        if face_result and os.path.exists(img_path):

            src_features = face_recognition.face_encodings(src_img)[0]

            ### find similar faces
            anchor_img = face_recognition.load_image_file(img_path)
            anchor_features = face_recognition.face_encodings(anchor_img)[0]
            find_result = face_recognition.compare_faces([src_features], anchor_features)
            ###

            _cbpf_data_model['msg']['NumberOfHuman']['value'] = len(face_result)
            _cbpf_data_model['msg']['DetectHuman']['value'] = face_result
            _cbpf_data_model['msg']['faceFound']['value'] = list(map(str,find_result))
            #_cbpf_data_model['msg']['source']['value'] = _img_64

        elif not face_result:
            print ("face is not contained the received image")
        elif os.path.exists(img_path) is False:
            print ("request image does not exist")
        else:
            pass
    else:
        pass

    print (json.dumps(_cbpf_data_model, indent=2))
    
    return _cbpf_data_model

if __name__ == "__main__":
    
    main()
