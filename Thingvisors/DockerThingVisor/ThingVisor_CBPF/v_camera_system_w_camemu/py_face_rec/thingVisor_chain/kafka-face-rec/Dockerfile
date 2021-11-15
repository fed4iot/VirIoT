FROM python:3.6.9-slim

RUN apt-get update -y
RUN apt update -y
RUN apt install -y libgl1-mesa-dev
RUN apt install -y libglib2.0-0
#RUN apt install -y vim
RUN apt install -y net-tools procps
RUN apt install -y cmake build-essential

COPY ./src /src

WORKDIR /src/

RUN pip3 install -r requirements.txt

ENTRYPOINT ["python3", "main.py"]
