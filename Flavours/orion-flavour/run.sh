#!/bin/bash

#
#Copyright Odin Solutions S.L. All Rights Reserved.
#
#SPDX-License-Identifier: Apache-2.0
#

exit_script() {
    echo "Printing something special!"
    echo "Maybe executing other commands!"
    
    trap - SIGINT SIGTERM SIGHUP # clear the trap

    echo "Stopping MongoDB..."
    /usr/bin/mongod --shutdown
    echo "Stopped MongoDB..."

    kill -- -$$ # Sends signal to child/sub processes (contextBroker and /home/node/app/index.js)
}

trap exit_script SIGINT SIGTERM SIGHUP #Define capture signals

# Initialize first run
if [[ -e /home/node/app/.firstrun ]]; then

    /home/node/app/first_run.sh
    
    echo "Launch MongoDB using auth..."

    /usr/bin/mongod --dbpath /data/db --auth $@ &
    while ! nc -vz localhost 27017; do sleep 1; done

    echo "MongoDB is running..."

else
    echo "Launch MongoDB without auth..."

    /usr/bin/mongod --dbpath /data/db &
    while ! nc -vz localhost 27017; do sleep 1; done

    echo "MongoDB is running..."
fi

echo "Launch Orion Context broker..."

/usr/bin/contextBroker -fg -multiservice -ngsiv1Autocast &
while ! nc -vz localhost 1026; do sleep 1; done

echo "Orion Context broker is running..."

echo "Launch Silos Controller..."

/usr/bin/node /home/node/app/index.js &

echo "All services are started."

child=$! 
wait "$child"

#echo "All services are stopped."

#sleep infinity