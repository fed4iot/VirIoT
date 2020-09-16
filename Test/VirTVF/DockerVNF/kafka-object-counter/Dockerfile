FROM python:3.6.9-slim

RUN apt update -y
#RUN apt install -y vim

COPY ./src /src

WORKDIR /src/

RUN pip3 install -r requirements.txt

ENTRYPOINT ["python3", "sfNode.py"]

