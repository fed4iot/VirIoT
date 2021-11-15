import os
import uuid
from time import sleep
import face_recognition

import json
import base64
import time
import datetime
from common import common

#img_path = "test.jpg"
temp = "temp.jpg"
UTC = datetime.timezone.utc

detect_model = "cnn"
#detect_model = "hog"

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
                            'source': {'type': 'Property', 'value': 'null'},
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

    timestamp = datetime.datetime.now(UTC).strftime('%Y-%m-%dT%H:%M:%S.%fZ')

    f_img = face_recognition.load_image_file(temp)
    result = face_recognition.face_locations(f_img, model=detect_model)

    _cbpf_data_model = cbpf_data_model

    _cbpf_data_model['id'] = 'urn:ngsi-ld:' + service_name + ':' + _src_name
    _cbpf_data_model['msg']['location'] = location
    _cbpf_data_model['msg']['createdAt']['value'] = timestamp

    if not result:
        pass
    else:
        _cbpf_data_model['msg']['NumberOfHuman']['value'] = len(result)
        _cbpf_data_model['msg']['DetectHuman']['value'] = result
        _cbpf_data_model['msg']['source']['value'] = _img_64

    _cbpf_data_model['msg']['dataProvider'] = dataProvider

    print (json.dumps(_cbpf_data_model, indent=2))
    
    return _cbpf_data_model

if __name__ == "__main__":
    
    main()
