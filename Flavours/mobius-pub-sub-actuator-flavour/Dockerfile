 # specify the node base image with your desired version node:<version>

FROM node:7.6

# MySQL
ENV MYSQL_PWD fed4iot
RUN echo "mysql-server mysql-server/root_password password $MYSQL_PWD" | debconf-set-selections
RUN echo "mysql-server mysql-server/root_password_again password $MYSQL_PWD" | debconf-set-selections
RUN apt-get update

RUN apt-get install -y --no-install-recommends mysql-server mosquitto mosquitto-clients screen python3-minimal python3-pip python3-setuptools  nano nodejs npm git sed 
RUN pip3 install paho-mqtt requests pymongo
RUN apt-get autoclean -y 
RUN apt-get autoremove -y

COPY . /app
WORKDIR /app/
RUN git clone https://github.com/IoTKETI/Mobius.git
WORKDIR /app/Mobius
RUN git checkout tags/2.4.0

RUN [ "/bin/bash", "/app/mobius_setup.sh" ]
RUN npm install

# Debug
RUN apt-get install -y --no-install-recommends openssh-server iproute2 vim pylint
COPY id_rsa.pub /root/.ssh/authorized_keys
EXPOSE 22
# End debug

ENTRYPOINT []

CMD [ "/bin/bash", "/app/start.sh" ]
# replace this with your application's default port
EXPOSE 7579
