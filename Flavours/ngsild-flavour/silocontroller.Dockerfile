### specify the node base image with your desired version node:<version>
FROM python:3

### environment for python silo controller able to talk to mongo and mosquitto and leveldb hashmap
### pymongo could go away if silocontroller only talks to mastercontroller
RUN pip3 paho-mqtt requests pymongo plyvel

COPY common_vsilo_functionality.py /
COPY ngsild_silo_controller.py /
COPY F4Ingsild.py /

CMD [ "python", "./ngsild_silo_controller.py" ]
