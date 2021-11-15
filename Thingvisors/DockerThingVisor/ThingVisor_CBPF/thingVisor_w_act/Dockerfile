 # specify the node base image with your desired version node:<version>

FROM python:3.6-slim

RUN apt update
RUN apt install -y screen
RUN pip3 install paho-mqtt flask requests pymongo jsonmerge

# Debug
# RUN apt -y install openssh-server iproute2 vim curl tar
# RUN pip3 install pylint
# COPY id_rsa.pub /root/.ssh/authorized_keys
# EXPOSE 22
# End debug

COPY ./src /app
WORKDIR /app

ENTRYPOINT []
CMD [ "/bin/bash", "./start.sh" ]
#EXPOSE 8089
