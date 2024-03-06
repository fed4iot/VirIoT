 # specify the node base image with your desired version node:<version>

FROM python:3.6-slim

RUN apt update
RUN apt -y install screen
RUN pip3 install paho-mqtt pymongo requests

COPY . /app
WORKDIR /app

ENTRYPOINT []
RUN ["chmod", "+x", "/app/start.sh"]
CMD /app/start.sh
