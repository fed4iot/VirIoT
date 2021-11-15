FROM python:3.6.9-slim

RUN apt-get update -y
RUN apt-get install -y libgl1-mesa-dev libglib2.0-0 libsm6 libxrender1 libxext6

COPY ./src /src
WORKDIR /src/

RUN pip3 install -r requirements.txt
