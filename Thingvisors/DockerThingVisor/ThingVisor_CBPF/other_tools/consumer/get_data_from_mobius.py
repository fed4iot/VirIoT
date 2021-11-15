#! /usr/bin/python3 

import requests
import json
import base64





url = "http://192.168.11.101:31910/Mobius/cbpf-logger:tokyo:01/cbpf-logger:tokyo:01/msg?rcn=4"


"""
payload = {
    "m2m:cin": {
        "con": {
				"cmd-value":"start",
				"cmd-qos":"2",
                                #"cmd-params": params
				#"cmd-id":"123456",
    
				}
    }
}
"""

headers = {
        'accept': "application/json",
        'x-m2m-ri': "12345",
        'x-m2m-origin': 'S',
        'content-type': "application/vnd.onem2m-res+json;ty=4",
        'cache-control': "no-cache",
}

#response = requests.request("POST", url, headers=headers, data = json.dumps(payload))
response = requests.request("GET", url, headers=headers)

print(response.text.encode('utf8'))
