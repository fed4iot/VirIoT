#!/bin/bash

docker build -t homethermometer-tv .
cd ../../../CLI
python3 f4i.py del-thingvisor -c http://$NODE_IP:$NODE_PORT -n homethermometertvlocal2 -f
python3 f4i.py add-thingvisor -c http://$NODE_IP:$NODE_PORT -n homethermometertvlocal2 -d "" -y "../yaml/thingVisor-homethermometer-local.yaml" -p '{"mode": "oregon","n2n_ip": "10.11.0.5", "community_domus": "clinica1", "domuskey": "clinica1", "supernode_ip": "18.188.136.98", "supernode_port": "7654", "backendUri": "http://10.11.0.2", "backendPort": "3600", "username": "admin@dsstaging.sferainnovazione.it", "password": "Sf3r4DS"}'
cd ../Thingvisors/DockerThingVisor/ThingVisor_HomeThermometer
sleep 3
kubectl get pods -o wide

