FROM python:3.6-slim
COPY . /app
WORKDIR /app
RUN mkdir data

RUN apt update

RUN apt install -y screen
RUN pip install -r requirements.txt

CMD [ "/bin/bash", "./start.sh" ]

EXPOSE 8090