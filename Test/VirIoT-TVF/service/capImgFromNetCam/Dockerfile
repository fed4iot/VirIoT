FROM python:3.6-slim

#RUN apt update -y
#RUN apt install -y vim

COPY ./src /src

WORKDIR /src/

#RUN pip install -r requirements.txt

ENTRYPOINT ["python3", "ftp.py"]
