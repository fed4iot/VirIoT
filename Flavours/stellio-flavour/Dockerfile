### specify the node base image with your desired version node:<version>
FROM ubuntu:18.04

### especially this disables the tzdata interactive asking
ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update
RUN apt-get -y upgrade
RUN apt-get install -y wget gnupg2 openjdk-11-jdk

### download Stellio
RUN apt-get install -y git
#remember in dockerfile 'cd' only lasts for 1 single line of RUN, use WORKDIR
WORKDIR /app
RUN git clone https://github.com/stellio-hub/stellio-context-broker.git
WORKDIR /app/stellio-context-broker

### disable neo4j migrations (temp)
RUN echo "org.neo4j.migrations.enabled=false" >> entity-service/src/main/resources/application.properties

### compile and assemble Stellio
RUN ./gradlew build --exclude-task test

### move created jars outside
RUN mkdir ../stellio/
RUN cp api-gateway/build/libs/api-gateway-0.5.0.jar ../stellio/
RUN cp entity-service/build/libs/entity-service-0.5.0.jar ../stellio/
RUN cp search-service/build/libs/search-service-0.5.0.jar ../stellio/
RUN cp subscription-service/build/libs/subscription-service-0.5.0.jar ../stellio/

### download and configure kafka and zookeeper
WORKDIR /app
RUN wget https://www-us.apache.org/dist/kafka/2.3.0/kafka_2.12-2.3.0.tgz
RUN tar xvfz kafka_2.12-2.3.0.tgz
RUN rm kafka_2.12-2.3.0.tgz
RUN echo "\nlisteners=PLAINTEXT://:29092" >> kafka_2.12-2.3.0/config/server.properties

### download and configure neo4j
RUN wget -O - https://debian.neo4j.com/neotechnology.gpg.key | apt-key add -
RUN echo 'deb https://debian.neo4j.com stable latest' | tee -a /etc/apt/sources.list.d/neo4j.list
RUN apt-get update
RUN apt-get install -y neo4j=1:4.0.5
RUN echo "dbms.default_database=stellio" >> /etc/neo4j/neo4j.conf
RUN neo4j-admin set-initial-password neo4j_password

### download and configure postgresql 10 and timescaledb 1.5.1
RUN apt-get install -y --no-install-recommends postgresql-10
RUN wget --content-disposition https://packagecloud.io/timescale/timescaledb/packages/debian/jessie/timescaledb-loader-postgresql-10_1.4.2~debian8_amd64.deb/download.deb
RUN wget --content-disposition https://packagecloud.io/timescale/timescaledb/packages/debian/jessie/timescaledb-oss-postgresql-10_1.4.2~debian8_amd64.deb/download.deb
RUN dpkg -i timescaledb-loader-postgresql-10_1.4.2~debian8_amd64.deb; exit 0
RUN apt --fix-broken install -y
RUN dpkg -i timescaledb-oss-postgresql-10_1.4.2~debian8_amd64.deb
RUN echo "shared_preload_libraries = 'timescaledb'" >> /etc/postgresql/10/main/postgresql.conf

USER postgres
RUN /etc/init.d/postgresql start &&\
    psql -c "CREATE USER stellio_subscription;" &&\
    psql -c "CREATE USER stellio_search;" &&\
    psql -c "ALTER USER stellio_subscription WITH PASSWORD 'stellio_subscription_db_password';" &&\
    psql -c "ALTER USER stellio_search WITH PASSWORD 'stellio_search_db_password';" &&\
    psql -c "CREATE DATABASE stellio_subscription;" &&\
    psql -c "CREATE DATABASE stellio_search;" &&\
    psql -c "GRANT ALL PRIVILEGES ON DATABASE stellio_subscription TO stellio_subscription;" &&\
    psql -c "GRANT ALL PRIVILEGES ON DATABASE stellio_search TO stellio_search;" &&\
    psql -U "postgres" stellio_search -c "CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;" &&\
    psql -U "postgres" stellio_search -c "CREATE EXTENSION IF NOT EXISTS pgcrypto CASCADE;"
USER root

COPY . /app

### install things needed to run the silo
RUN apt-get install -y --no-install-recommends screen

### environment for python silo controller able to talk to mongo and mosquitto and leveldb hashmap
RUN apt-get install -y --no-install-recommends mosquitto-clients python3-minimal python3-pip python3-setuptools python3-wheel
RUN pip3 install setuptools wheel paho-mqtt requests pymongo plyvel

### cleanup
RUN rm -rf stellio-context-broker timescaledb-loader-postgresql-10_1.4.2~debian8_amd64.deb timescaledb-oss-postgresql-10_1.4.2~debian8_amd64.deb
RUN apt-get purge -y wget gnupg2 openjdk-11-jdk git
RUN apt-get autoclean -y
RUN apt-get autoremove -y
RUN rm -rf plyvelhashmap
RUN rm -rf __pycache__

ENTRYPOINT []
CMD /app/start.sh

# replace this with your application's default port
EXPOSE 9090
