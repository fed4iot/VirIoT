#!/bin/bash
exec >/dev/tty 2>/dev/tty </dev/tty && screen -S zookeeper -s /bin/bash -t win0 -A -d -m
#exec >/dev/tty 2>/dev/tty </dev/tty && screen -S kafka -s /bin/bash -t win0 -A -d -m
#exec >/dev/tty 2>/dev/tty </dev/tty && screen -S postgresql -s /bin/bash -t win0 -A -d -m
#exec >/dev/tty 2>/dev/tty </dev/tty && screen -S neo4j -s /bin/bash -t win0 -A -d -m
#exec >/dev/tty 2>/dev/tty </dev/tty && screen -S api-gateway -s /bin/bash -t win0 -A -d -m
#exec >/dev/tty 2>/dev/tty </dev/tty && screen -S search-service -s /bin/bash -t win0 -A -d -m
#exec >/dev/tty 2>/dev/tty </dev/tty && screen -S subscription-service -s /bin/bash -t win0 -A -d -m
#exec >/dev/tty 2>/dev/tty </dev/tty && screen -S entity-service -s /bin/bash -t win0 -A -d -m
#exec >/dev/tty 2>/dev/tty </dev/tty && screen -S silocontroller -s /bin/bash -t win0 -A -d -m
#
#echo "Starting zookeeper"
#screen -S zookeeper -p win0 -X stuff $'kafka_2.12-2.3.0/bin/zookeeper-server-start.sh kafka_2.12-2.3.0/config/zookeeper.properties\n'
#sleep 20
#echo "Zookeeper started"
#echo "Starting kafka"
#screen -S kafka -p win0 -X stuff $'kafka_2.12-2.3.0/bin/kafka-server-start.sh kafka_2.12-2.3.0/config/server.properties\n'
#sleep 20
#echo "Kafka started"
#echo "Starting postgresql"
#screen -S postgres -p win0 -X stuff $'/etc/init.d/postgresql start\n'
#sleep 20
#echo "Postgresql started"
#echo "Starting neo4j"
#screen -S neo4j -p win0 -X stuff $'service neo4j start\n'
#sleep 20
#echo "Neo4j started"
#echo "Starting gateway"
#screen -S api-gateway -p win0 -X stuff $'java -Xms512m -jar stellio/api-gateway-*.jar\n'
#sleep 20
#echo "Gateway started"
#echo "Starting search service"
#screen -S search-service -p win0 -X stuff $'java -Xms512m -jar stellio/search-service-*.jar\n'
#sleep 20
#echo "Search service started"
#echo "Starting subscription service"
#screen -S subscription-service -p win0 -X stuff $'java -Xms512m -jar stellio/subscription-service-*.jar\n'
#sleep 20
#echo "Subscription service started"
#echo "Starting entity service"
#screen -S entity-service -p win0 -X stuff $'java -Xms512m -jar stellio/entity-service-*.jar\n'
#sleep 20
#echo "Entity service started"
#echo "Starting silo controller"
#screen -S silocontroller -p win0 -X stuff $'python3 stellio_silo_controller.py\n'
#sleep 20
#echo "Silo controller started"
sleep infinity
