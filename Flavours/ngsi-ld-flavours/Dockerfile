### specify the node base image with your desired version node:<version>
FROM python:3.8-slim

### environment for python silo controller able to talk to mongo and mosquitto and leveldb hashmap
### pymongo could go away if silocontroller only talks to mastercontroller

### RUN apt update && apt -y upgrade
### RUN apt install -y screen
RUN pip3 install paho-mqtt requests pymongo plyvel flask uuid

COPY . /app
WORKDIR /app

CMD [ "python3", "./ngsild_silo_controller.py" ]
