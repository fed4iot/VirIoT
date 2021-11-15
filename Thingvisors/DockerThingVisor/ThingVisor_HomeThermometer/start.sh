#!/bin/bash

# Debug
# service ssh start
# env >> /etc/environment
# end Debug

echo $params > test.json
jq -r 'to_entries|map("\(.key)=\(.value|tostring)")|.[]' test.json > params.cfg

source params.cfg
if [ ! -z $n2n_ip ] & [ ! -z $community_domus ] & [ ! -z $domuskey ] & [ ! -z $supernode_ip] & [ ! -z $supernode_port ]; then 
        echo "Setting up N2N";
        edge -r -a $n2n_ip -c $community_domus -k $domuskey -l $supernode_ip:$supernode_port
        sleep 5
else 
        echo "Not all the params were given. I'm not setting up N2N."; 
fi

rm test.json
rm params.cfg

/usr/bin/screen -S thingVisor -s /bin/bash -t win0 -A -d -m
screen -S thingVisor -p win0 -X stuff $'/usr/local/bin/python3 /app/thingVisor_homethermometer.py \n'

sleep infinity
