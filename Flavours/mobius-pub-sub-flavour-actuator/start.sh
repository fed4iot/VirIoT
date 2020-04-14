#!/bin/bash
service mysql start
service mosquitto start

# Debug
service ssh start
env >> /etc/environment
# End debug

if [ ! -f /app/mobiusdb ]
    then
        echo "mobius db already there...."
        mysql -u root -pfed4iot < mobius/mobiusdb.sql
        touch /app/mobiusdb
fi

/usr/bin/screen -S mobius -s /bin/bash -t win0 -A -d -m
/usr/bin/screen -S vEnv_controller -s /bin/bash -t win0 -A -d -m

screen -S mobius -p win0 -X stuff $'node mobius.js\n'
sleep 7
screen -S vEnv_controller -p win0 -X stuff $'/usr/bin/python3 /app/mobius_pub_sub_silo_controller.py\n'

sleep infinity
