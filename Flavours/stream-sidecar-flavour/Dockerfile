 # specify the node base image with your desired version node:<version>

FROM python:3.6-slim

RUN apt update
RUN apt install -y screen mosquitto mosquitto-clients
RUN pip3 install paho-mqtt requests pymongo flask

COPY . /app
WORKDIR /app

# Debug
# RUN apt-get install -y --no-install-recommends openssh-server iproute2 vim pylint
# COPY id_rsa.pub /root/.ssh/authorized_keys
# EXPOSE 22
# End debug

ENTRYPOINT []
#CMD /app/start.sh
CMD ["/bin/bash", "./start.sh"]
EXPOSE 80
