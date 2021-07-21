#
#Copyright Odin Solutions S.L. All Rights Reserved.
#
#SPDX-License-Identifier: Apache-2.0
#

FROM ubuntu:18.04

RUN apt-get update -y

#Install python3
RUN apt-get install software-properties-common -y
RUN add-apt-repository ppa:deadsnakes/ppa
RUN apt-get install python3 -y

#Install pip3
RUN apt-get install python3-pip -y

#Install java JRE
RUN apt-get install openjdk-11-jre -y
#or 
#RUN apt install default-jre -y --> It works but is not used to have control about the version.

#Install utils
RUN apt-get install net-tools -y
RUN apt-get install vim -y
RUN apt-get install curl -y

# Establish workdir
WORKDIR /opt/API-CM

#Transfer source and neccesary files
COPY API-CM.py config.cfg CapabilityGenerator.jar ./
COPY config ./config
COPY local_dependencies ./local_dependencies
COPY certs ./certs

#KeyRock endpoint
ENV keyrock_protocol=https
ENV keyrock_host=keyrock
ENV keyrock_port=443
ENV PDP_URL=https://pdphost:8080/XACMLServletPDP/

# application's default port
EXPOSE 3030

# Launch app
CMD [ "python3", "/opt/API-CM/API-CM.py" ]