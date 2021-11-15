import requests
import json
import ast

API = "latest"

def getContentFromOpenMTC(end_point, resource):

    rest_api = end_point + '/' + resource + '/' + API

    print (rest_api)

    response = requests.get(rest_api)

    print (response)

    result = response.json()
    content = result['m2m:cin']['con']

    #str -> dict
    #print (content)

    content = ast.literal_eval(content)

    return content
