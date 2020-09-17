FROM python:3.6.9-slim

RUN apt update -y
#RUN apt install -y vim

RUN apt install -y libgl1-mesa-dev libglib2.0-0

COPY ./src /src

WORKDIR /src/

RUN pip install -r requirements.txt

ENTRYPOINT ["python3", "main.py"]
