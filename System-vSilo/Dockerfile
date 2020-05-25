### specify the node base image with your desired version node:<version>
FROM ubuntu:18.04

### especially this disables the tzdata interactive asking
ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update
RUN apt-get -y upgrade

### get and compile Scorpio
RUN apt-get install -y git
#remember in dockerfile 'cd' only lasts for 1 single line of RUN, use WORKDIR
WORKDIR /app
RUN git clone https://github.com/ScorpioBroker/ScorpioBroker.git
WORKDIR /app/ScorpioBroker
RUN apt-get install -y openjdk-8-jdk-headless
RUN apt-get install -y maven
RUN mvn clean package -DskipTests

RUN rm -rf /root/.m2
RUN apt-get purge -y maven openjdk-8-jdk-headless

### move created jars outside
RUN mkdir ../scorpiobroker
RUN cp SpringCloudModules/eureka/target/eureka-server-0.9.2-SNAPSHOT.jar ../scorpiobroker/
RUN cp SpringCloudModules/gateway/target/gateway-0.9.2-SNAPSHOT.jar ../scorpiobroker/
RUN cp SpringCloudModules/config-server/target/config-server-0.9.2-SNAPSHOT.jar ../scorpiobroker/

### now either copy the microservices' jars...
RUN cp Storage/StorageManager/target/StorageManager-0.9.2-SNAPSHOT.jar ../scorpiobroker/
RUN cp Core/QueryManager/target/QueryManager-0.9.2-SNAPSHOT.jar ../scorpiobroker/
RUN cp Registry/RegistryManager/target/RegistryManager-0.9.2-SNAPSHOT.jar ../scorpiobroker/
RUN cp Core/EntityManager/target/EntityManager-0.9.2-SNAPSHOT.jar ../scorpiobroker/
RUN cp History/HistoryManager/target/HistoryManager-0.9.2-SNAPSHOT.jar ../scorpiobroker/
RUN cp Core/SubscriptionManager/target/SubscriptionManager-0.9.2-SNAPSHOT.jar ../scorpiobroker/
RUN cp Core/AtContextServer/target/AtContextServer-0.9.2-SNAPSHOT.jar ../scorpiobroker/

### OR the aio runner
#RUN cp AllInOneRunner/target/AllInOneRunner-0.9.2-SNAPSHOT.jar ../scorpiobroker/

### download kafka binaries and cleanup
WORKDIR /app
RUN apt-get install -y wget
RUN wget https://www-us.apache.org/dist/kafka/2.3.0/kafka_2.12-2.3.0.tgz
RUN tar xvfz kafka_2.12-2.3.0.tgz
RUN rm kafka_2.12-2.3.0.tgz
RUN rm -rf ScorpioBroker
RUN apt-get purge -y wget

### install jre to run scorpio
RUN apt-get install -y openjdk-8-jre-headless

### install things needed to run the silo
RUN apt-get install -y --no-install-recommends screen

### environment for python silo controller able to talk to mongo and mosquitto and leveldb hashmap
RUN apt-get install -y --no-install-recommends mosquitto-clients python3-minimal python3-pip python3-setuptools python3-wheel
RUN pip3 install setuptools wheel paho-mqtt requests pymongo plyvel

### postgres
ENV POSTGRES_USER ngb
ENV POSTGRES_PASSWORD ngb
ENV POSTGRES_DB ngb
####### RUN apt-get install -y --no-install-recommends postgresql-common postgresql-client-common
####### unable to make the following command accept the -y option to run headless!!!!
####### hence not able to install the postgres repositories for latest version
####### RUN ["/usr/share/postgresql-common/pgdg/apt.postgresql.org.sh", "-y"]
RUN apt-get install -y --no-install-recommends postgresql-10
RUN apt-get install -y --no-install-recommends postgresql-10-postgis-2.4 postgresql-10-postgis-scripts

RUN apt-get autoclean -y 
RUN apt-get autoremove -y

USER postgres
### we use && to run commands in sequence
RUN /etc/init.d/postgresql start &&\
    psql -c "create user $POSTGRES_USER superuser createdb password '$POSTGRES_PASSWORD';" &&\
    psql -c "create database $POSTGRES_DB owner = $POSTGRES_USER;" &&\
    psql -c "create database gisdb;" &&\
    psql -c "\connect gisdb" -c "; CREATE SCHEMA postgis; ALTER DATABASE gisdb SET search_path=public, postgis, contrib; CREATE EXTENSION postgis SCHEMA postgis;"

USER root
COPY . /app
### reconstruct the folder structure of the github fed4iot
### (not needed anymore. For now all files in the same folder)
######RUN mkdir scorpio-flavour
######RUN mv /app/scorpio_silo_controller.py /app/scorpio-flavour/
######RUN mv /app/F4Ingsild.py /app/scorpio-flavour/
#COPY ../common_vsilo_functionality.py /app # THIS MUST BE DONE OUTSIDE OF DOCKERFILE
RUN rm -rf plyvelhashmap
RUN rm -rf __pycache__

ENTRYPOINT []
CMD /app/start.sh

# replace this with your application's default port
EXPOSE 9090
