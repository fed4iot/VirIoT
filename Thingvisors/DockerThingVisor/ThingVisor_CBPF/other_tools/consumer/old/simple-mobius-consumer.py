#! /usr/bin/python3 

import requests
import json

#url = "http://172.17.0.4:7579/Mobius/helloWorldActuator:Lamp01/helloWorldActuator:Lamp01/set-color"
url = "http://192.168.11.101:31910/Mobius/cbpf:tokyo:01/cbpf:tokyo:01/"

#url = "http://192.168.11.101:31910/Mobius/helloworldtv:Lamp01"

payload = {
    "m2m:cin": {
        "con": {
				"cmd-value":"blue",
				"cmd-qos":"2"
				#"cmd-id":"123456",
    
				}
    }
}


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
