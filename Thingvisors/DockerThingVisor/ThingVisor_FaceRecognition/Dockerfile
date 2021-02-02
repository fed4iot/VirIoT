 # specify the node base image with your desired version node:<version>

FROM python:3.6-slim

RUN apt update
RUN apt -y install screen
RUN apt -y install libmagic1

COPY . /app
WORKDIR /app
RUN pip3 install -r requirements.txt

ENTRYPOINT []

CMD [ "/bin/bash", "./start.sh" ]

EXPOSE 5000
