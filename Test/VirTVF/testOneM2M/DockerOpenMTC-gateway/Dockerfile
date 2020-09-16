FROM python:2.7-slim

RUN apt update -y
RUN apt install -y vim
RUN apt install -y libev-dev gcc make automake

COPY ./openmtc /openmtc

WORKDIR /openmtc/openmtc-gevent/

RUN pip install -r ./dependencies.txt

ENTRYPOINT ["./run-gateway"]
