'''
Azure API 環境設定
author：
datetime：2021.2.20
'''
# !/usr/bin/python
# -*- coding: utf-8 -*-
from azure.cognitiveservices.vision.face import FaceClient
from msrest.authentication import CognitiveServicesCredentials

# This key will serve all examples in this document.
#KEY = "6dddf85ffb3445f288d01cb8a1d0457b"
KEY = "90b3d7807d914a26a581c08ab0a82ba5"
#KEY = "a621f8126fe34801a25e53ded5ba5cb8"

# This endpoint will be used in all examples in this quickstart.
#ENDPOINT = "https://fed4iot.cognitiveservices.azure.com/"
ENDPOINT = "https://fed4iot-face-api.cognitiveservices.azure.com/"
#ENDPOINT = "https://fed4iot-face-api-eu.cognitiveservices.azure.com/"

# Create an authenticated FaceClient.
face_client = FaceClient(ENDPOINT, CognitiveServicesCredentials(KEY))
