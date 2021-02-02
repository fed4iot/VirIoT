#!/bin/bash

docker build -t facerecognition-tv .
cd ../../../CLI
python3 f4i.py del-thingvisor -n facerecognition -f
python3 f4i.py add-thingvisor -i facerecognition-tv:latest -n facerecognition -d "faceRecognition thingVisor" -p '{"num_of_cameras":30, "robot_ip": "10", "robot_port": "20"}'
cd ../Thingvisors/DockerThingVisor/ThingVisor_FaceRecognition
sleep 3
docker exec -it facerecognition bash

