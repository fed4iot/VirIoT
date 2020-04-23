 # specify the node base image with your desired version node:<version>

FROM python:3.6-slim

RUN apt update
RUN apt -y install screen

COPY . /app
WORKDIR /app
RUN pip3 install -r requirements.txt

ENTRYPOINT []
CMD /app/start.sh
