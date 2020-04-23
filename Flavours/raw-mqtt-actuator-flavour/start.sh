#!/bin/bash
service mosquitto start

# Debug
# service ssh start
# env >> /etc/environment
# End debug

/usr/bin/screen -S thingvisor -s /bin/bash -t win0 -A -d -m
screen -S thingvisor -p win0 -X stuff $'/usr/local/bin/python3 /app/raw_vSilo_controller.py \n'

sleep infinity
