 # specify the node base image with your desired version node:<version>

FROM python:3.6-slim

RUN apt update && apt upgrade -y
RUN apt install -y jq
RUN apt install -y screen
RUN apt install -y git
RUN apt install -y build-essential
RUN apt install -y autoconf
RUN apt install -y pkg-config
RUN pip3 install paho-mqtt flask requests pymongo jsonmerge

WORKDIR /app
RUN git clone https://github.com/ntop/n2n.git --branch 2.8-stable --single-branch n2n

WORKDIR /app/n2n
RUN ./autogen.sh
RUN ./configure
RUN make
RUN make install

COPY . /app

WORKDIR /app

CMD [ "/bin/bash", "./start.sh" ]
EXPOSE 8089
