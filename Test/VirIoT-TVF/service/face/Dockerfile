FROM python:3.6-slim

#RUN apt update -y
#RUN apt install -y vim

COPY ./face /face

WORKDIR /face/

#RUN pip install -r requirements.txt

ENTRYPOINT ["python3", "face.py"]
