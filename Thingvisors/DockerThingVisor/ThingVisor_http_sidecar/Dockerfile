 # specify the node base image with your desired version node:<version>

FROM python:3.6-slim

RUN apt update
RUN apt install -y screen
RUN pip3 install flask requests paho-mqtt
COPY . /app
WORKDIR /app

ENTRYPOINT []
EXPOSE 5001

CMD [ "/bin/bash", "./start.sh" ]
