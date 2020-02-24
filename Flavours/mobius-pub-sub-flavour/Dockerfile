 # specify the node base image with your desired version node:<version>

#FROM node:8.12.0
FROM ubuntu:18.04


# MySQL
ENV MYSQL_PWD fed4iot
RUN echo "mysql-server mysql-server/root_password password $MYSQL_PWD" | debconf-set-selections
RUN echo "mysql-server mysql-server/root_password_again password $MYSQL_PWD" | debconf-set-selections
RUN apt-get update
#RUN apt-get install -y --no-install-recommends curl python-software-properties
#RUN "curl -s https://deb.nodesource.com/gpgkey/nodesource.gpg.key | apt-key add -"
#RUN "echo deb https://deb.nodesource.com/node_8.x xenial main > /etc/apt/sources.list.d/nodesource.list"
#RUN /app/nodesource_setup.sh
#RUN apt-get update
RUN apt-get install -y --no-install-recommends mysql-server mosquitto mosquitto-clients screen python3-minimal python3-pip python3-setuptools  nano nodejs npm
RUN pip3 install paho-mqtt requests pymongo
RUN apt-get install git sed -y
RUN apt-get autoclean -y 
RUN apt-get autoremove -y

COPY . /app
WORKDIR /app/
RUN git clone https://github.com/IoTKETI/Mobius.git
WORKDIR /app/Mobius
RUN git checkout tags/2.4.0

RUN [ "/bin/bash", "/app/mobius_setup.sh" ]
RUN npm install

ENTRYPOINT []

CMD [ "/bin/bash", "/app/start.sh" ]
# replace this with your application's default port
EXPOSE 7579
