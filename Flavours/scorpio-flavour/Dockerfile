 # specify the node base image with your desired version node:<version>

FROM openjdk:11-jre

RUN apt-get update

RUN apt-get install -y --no-install-recommends screen

# environment for python silo controller able to talk to mongo and mosquitto
RUN apt-get install -y --no-install-recommends mosquitto-clients python3-minimal python3-pip python3-setuptools python3-wheel
RUN pip3 install setuptools wheel paho-mqtt requests pymongo #############plyvel

# postgres
ENV POSTGRES_USER ngb
ENV POSTGRES_PASSWORD ngb
ENV POSTGRES_DB ngb
RUN apt-get install -y --no-install-recommends postgresql-common postgresql-client-common
# unable to make the following command accept the -y option to run headless!!!!
# hence not able to install the postgres repositories for latest version
#RUN ["/usr/share/postgresql-common/pgdg/apt.postgresql.org.sh", "-y"]
RUN apt-get install -y --no-install-recommends postgresql
RUN apt-get install -y --no-install-recommends postgresql-9.6-postgis-2.3 postgresql-9.6-postgis-scripts postgis

RUN apt-get autoclean -y 
RUN apt-get autoremove -y

USER postgres
# we use && to run commands in sequence
RUN /etc/init.d/postgresql start &&\
    psql -c "create user $POSTGRES_USER superuser createdb password '$POSTGRES_PASSWORD';" &&\
    psql -c "create database $POSTGRES_DB owner = $POSTGRES_USER;" &&\
    psql -c "create database gisdb;" &&\
    psql -c "\connect gisdb" -c "; CREATE SCHEMA postgis; ALTER DATABASE gisdb SET search_path=public, postgis, contrib; CREATE EXTENSION postgis SCHEMA postgis;"

USER root
COPY . /app
WORKDIR /app

ENTRYPOINT []
CMD /app/start.sh
# replace this with your application's default port
EXPOSE 9090
