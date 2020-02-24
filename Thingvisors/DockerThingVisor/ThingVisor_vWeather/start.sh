#!/bin/bash

/usr/bin/screen -S hypervisor -s /bin/bash -t win0 -A -d -m
screen -S hypervisor -p win0 -X stuff $'/usr/local/bin/python3 /app/thingVisor_weather.py \n'

sleep infinity
