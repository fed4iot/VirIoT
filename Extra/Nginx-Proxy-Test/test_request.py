#!/usr/bin/env python3
import requests
import sys

silo_service_ip = "10.106.81.172"

uri = "http://%s/vstream/relay-tv/timestamp/%s" % (silo_service_ip, str(sys.argv[1]))

headers = {"Cache-Control":"no-cache", "Content-Type":"txt/html"}

try:
    req = requests.get(uri, headers=headers)
    print(req.status_code)
    print(req.headers)
except Exception as err:
    print(err)
