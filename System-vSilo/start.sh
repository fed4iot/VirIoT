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
#exec >/dev/tty 2>/dev/tty </dev/tty && screen -S scorpioallinone -s /bin/bash -t win0 -A -d -m
exec >/dev/tty 2>/dev/tty </dev/tty && screen -S silocontroller -s /bin/bash -t win0 -A -d -m

screen -S zookeeper -p win0 -X stuff $'kafka_2.12-2.3.0/bin/zookeeper-server-start.sh kafka_2.12-2.3.0/config/zookeeper.properties\n'
sleep 10
screen -S kafka -p win0 -X stuff $'kafka_2.12-2.3.0/bin/kafka-server-start.sh kafka_2.12-2.3.0/config/server.properties\n'
sleep 10
screen -S eureka -p win0 -X stuff $'java -Xmx2g -jar scorpiobroker/eureka-server-0.9.2-SNAPSHOT.jar\n'
sleep 10
screen -S gateway -p win0 -X stuff $'java -Xmx2g -jar scorpiobroker/gateway-0.9.2-SNAPSHOT.jar\n'
sleep 10
screen -S config -p win0 -X stuff $'java -Xmx2g -jar scorpiobroker/config-server-0.9.2-SNAPSHOT.jar\n'
sleep 10
screen -S StorageM -p win0 -X stuff $'java -Xmx2g -jar scorpiobroker/StorageManager-0.9.2-SNAPSHOT.jar\n'
sleep 10
screen -S QueryM -p win0 -X stuff $'java -Xmx2g -jar scorpiobroker/QueryManager-0.9.2-SNAPSHOT.jar\n'
sleep 10
screen -S RegistryM -p win0 -X stuff $'java -Xmx2g -jar scorpiobroker/RegistryManager-0.9.2-SNAPSHOT.jar\n'
sleep 10
screen -S EntityM -p win0 -X stuff $'java -Xmx2g -jar scorpiobroker/EntityManager-0.9.2-SNAPSHOT.jar\n'
sleep 10
screen -S HistoryM -p win0 -X stuff $'java -Xmx2g -jar scorpiobroker/HistoryManager-0.9.2-SNAPSHOT.jar\n'
sleep 10
screen -S SubscriptionM -p win0 -X stuff $'java -Xmx2g -jar scorpiobroker/SubscriptionManager-0.9.2-SNAPSHOT.jar\n'
sleep 10
screen -S AtContextM -p win0 -X stuff $'java -Xmx2g -jar scorpiobroker/AtContextServer-0.9.2-SNAPSHOT.jar\n'
#sleep 10
#screen -S scorpioallinone -p win0 -X stuff $'java -Xmx2g -Dspring.profiles.active=local -jar scorpiobroker/AllInOneRunner-0.9.2-SNAPSHOT.jar\n'
sleep 10
screen -S silocontroller -p win0 -X stuff $'python3 scorpio_silo_controller.py\n'

sleep infinity
