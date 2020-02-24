#!/bin/bash

/usr/bin/screen -S hypervisor -s /bin/bash -t win0 -A -d -m
screen -S hypervisor -p win0 -X stuff $'/usr/local/bin/python3 /app/master-controller.py \n'
#screen -S hypervisor -p win0 -X stuff $'/usr/local/bin/python3 /app/flask-server.py \n'

sleep infinity

