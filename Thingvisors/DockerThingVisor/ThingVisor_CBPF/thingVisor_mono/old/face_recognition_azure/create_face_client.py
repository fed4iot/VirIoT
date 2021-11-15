'''
Azure API 環境設定
author：
datetime：2021.2.20
'''
# !/usr/bin/python
# -*- coding: utf-8 -*-
from azure.cognitiveservices.vision.face import FaceClient
from msrest.authentication import CognitiveServicesCredentials
import os
import json
import thingVisor_generic_module as thingvisor

# This key will serve all examples in this document.
# KEY = "6dddf85ffb3445f288d01cb8a1d0457b"
# KEY = os.environ['AZURE_KEY']
try:
    parameters = json.loads(os.environ['params'])
except json.decoder.JSONDecodeError:
    print("error on params (JSON) decoding" + "\n")
    exit()
except Exception as e:
    print("Error: Parameters not found", e)
    exit()

KEY = parameters["AZURE_KEY"]
# This endpoint will be used in all examples in this quickstart.
#ENDPOINT = "https://fed4iot.cognitiveservices.azure.com/"
ENDPOINT = parameters["ENDPOINT"]

# Create an authenticated FaceClient.
face_client = FaceClient(ENDPOINT, CognitiveServicesCredentials(KEY))
