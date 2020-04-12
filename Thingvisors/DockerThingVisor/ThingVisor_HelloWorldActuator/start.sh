#!/bin/bash
service ssh start
env >> /etc/environment
/usr/bin/screen -S thingVisor -s /bin/bash -t win0 -A -d -m
screen -S thingVisor -p win0 -X stuff $'/usr/local/bin/python3 /app/thingVisor_helloActuator.py \n'

sleep infinity
