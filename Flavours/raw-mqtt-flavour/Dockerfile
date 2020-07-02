 # specify the node base image with your desired version node:<version>

FROM python:3.6-slim

RUN apt update
RUN apt install -y screen mosquitto mosquitto-clients
RUN pip3 install paho-mqtt requests pymongo

COPY . /app
WORKDIR /app

ENTRYPOINT []
#CMD /app/start.sh
CMD ["/bin/bash", "./start.sh"]
EXPOSE 1883 9001