#!/bin/bash

docker build -t camerabot-tv .
cd ../../../CLI
python3 f4i.py del-thingvisor -n camerabot -f
python3 f4i.py add-thingvisor -i camerabot-tv:latest -n camerabot -d "cameraBot thingVisor" -p '{"num_of_cameras":30, "robot_ip": "10", "robot_port": "20"}'
cd ../Thingvisors/DockerThingVisor/ThingVisor_CameraBot
sleep 3
docker exec -it camerabot bash

