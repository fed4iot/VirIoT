#!/bin/bash
service mosquitto start

# Debug
# service ssh start
# env >> /etc/environment
# End debug

/usr/bin/screen -S proxy -s /bin/bash -t win0 -A -d -m
screen -S proxy -p win0 -X stuff $'/usr/local/bin/python3 /app/vStreamproxy.py \n'
sleep infinity
