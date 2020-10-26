#!/usr/bin/env python3
import requests
import sys

silo_service_ip = "10.106.81.172"
# silo_service_ip = "160.80.103.206:30838"

# uri = "http://%s/vstream/relay-tv/timestamp/%s" % (silo_service_ip, str(sys.argv[1]))
uri = "http://%s/vstream/relay-tv-ws/video/%s" % (silo_service_ip, str(sys.argv[1]))

headers = {"Content-Type":"txt/html"}
# headers = {"Cache-Control":"no-cache", "Content-Type":"txt/html"}

try:
    req = requests.get(uri, headers=headers)
    print(req.status_code)
    print(req.headers)
    print("File (len %d):" % len(req.text), req.text if len(req.text) < 20 else "")
except Exception as err:
    print(err)
