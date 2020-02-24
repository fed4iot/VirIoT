#!/bin/bash
/etc/init.d/postgresql start
exec >/dev/tty 2>/dev/tty </dev/tty && screen -S zookeeper -s /bin/bash -t win0 -A -d -m
exec >/dev/tty 2>/dev/tty </dev/tty && screen -S kafka -s /bin/bash -t win0 -A -d -m
exec >/dev/tty 2>/dev/tty </dev/tty && screen -S eureka -s /bin/bash -t win0 -A -d -m
exec >/dev/tty 2>/dev/tty </dev/tty && screen -S gateway -s /bin/bash -t win0 -A -d -m
exec >/dev/tty 2>/dev/tty </dev/tty && screen -S config -s /bin/bash -t win0 -A -d -m
exec >/dev/tty 2>/dev/tty </dev/tty && screen -S StorageM -s /bin/bash -t win0 -A -d -m
exec >/dev/tty 2>/dev/tty </dev/tty && screen -S QueryM -s /bin/bash -t win0 -A -d -m
exec >/dev/tty 2>/dev/tty </dev/tty && screen -S RegistryM -s /bin/bash -t win0 -A -d -m
exec >/dev/tty 2>/dev/tty </dev/tty && screen -S EntityM -s /bin/bash -t win0 -A -d -m
exec >/dev/tty 2>/dev/tty </dev/tty && screen -S HistoryM -s /bin/bash -t win0 -A -d -m
exec >/dev/tty 2>/dev/tty </dev/tty && screen -S SubscriptionM -s /bin/bash -t win0 -A -d -m
exec >/dev/tty 2>/dev/tty </dev/tty && screen -S AtContextM -s /bin/bash -t win0 -A -d -m
exec >/dev/tty 2>/dev/tty </dev/tty && screen -S silocontroller -s /bin/bash -t win0 -A -d -m

screen -S zookeeper -p win0 -X stuff $'kafka_2.12-2.3.0/bin/zookeeper-server-start.sh kafka_2.12-2.3.0/config/zookeeper.properties\n'
sleep 4
screen -S kafka -p win0 -X stuff $'kafka_2.12-2.3.0/bin/kafka-server-start.sh kafka_2.12-2.3.0/config/server.properties\n'
sleep 4
screen -S eureka -p win0 -X stuff $'java -Xmx2g -jar ScorpioBroker/SpringCloudModules/eureka/target/eureka-server-0.9.2-SNAPSHOT.jar\n'
sleep 4
screen -S gateway -p win0 -X stuff $'java -Xmx2g -jar ScorpioBroker/SpringCloudModules/gateway/target/gateway-0.9.2-SNAPSHOT.jar\n'
sleep 4
screen -S config -p win0 -X stuff $'java -Xmx2g -jar ScorpioBroker/SpringCloudModules/config-server/target/config-server-0.9.2-SNAPSHOT.jar\n'
sleep 4
screen -S StorageM -p win0 -X stuff $'java -Xmx2g -jar ScorpioBroker/Storage/StorageManager/target/StorageManager-0.9.2-SNAPSHOT.jar\n'
sleep 4
screen -S QueryM -p win0 -X stuff $'java -Xmx2g -jar ScorpioBroker/Core/QueryManager/target/QueryManager-0.9.2-SNAPSHOT.jar\n'
sleep 4
screen -S RegistryM -p win0 -X stuff $'java -Xmx2g -jar ScorpioBroker/Registry/RegistryManager/target/RegistryManager-0.9.2-SNAPSHOT.jar\n'
sleep 4
screen -S EntityM -p win0 -X stuff $'java -Xmx2g -jar ScorpioBroker/Core/EntityManager/target/EntityManager-0.9.2-SNAPSHOT.jar\n'
sleep 4
screen -S HistoryM -p win0 -X stuff $'java -Xmx2g -jar ScorpioBroker/History/HistoryManager/target/HistoryManager-0.9.2-SNAPSHOT.jar\n'
sleep 4
screen -S SubscriptionM -p win0 -X stuff $'java -Xmx2g -jar ScorpioBroker/Core/SubscriptionManager/target/SubscriptionManager-0.9.2-SNAPSHOT.jar\n'
sleep 4
screen -S AtContextM -p win0 -X stuff $'java -Xmx2g -jar ScorpioBroker/Core/AtContextServer/target/AtContextServer-0.9.2-SNAPSHOT.jar\n'
sleep 4
screen -S silocontroller -p win0 -X stuff $'python3 scorpio_silo_controller\n'

sleep infinity

