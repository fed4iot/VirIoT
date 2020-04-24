 # specify the node base image with your desired version node:<version>

FROM python:3.6-slim

RUN apt update
RUN apt -y install screen
RUN pip3 install paho-mqtt requests pymongo jsonmerge

COPY . /app
WORKDIR /app

ENTRYPOINT []
CMD /app/start.sh
