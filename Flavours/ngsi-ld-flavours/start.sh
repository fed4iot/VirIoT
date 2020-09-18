#!/bin/bash

exec >/dev/tty 2>/dev/tty </dev/tty && screen -S silocontroller -s /bin/bash -t win0 -A -d -m
screen -S silocontroller -p win0 -X stuff $'/usr/bin/python3 ./ngsild_silo_controller.py\n'

sleep infinity
