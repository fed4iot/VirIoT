#!/bin/bash
service mosquitto start

/usr/bin/screen -S hypervisor -s /bin/bash -t win0 -A -d -m
screen -S hypervisor -p win0 -X stuff $'/usr/local/bin/python3 /app/raw_vSilo_controller.py \n'

sleep infinity
