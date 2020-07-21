# License

ThingVisor source code files are made avaialable under the Apache License, Version 2.0 (Apache-2.0), located into the LICENSE file.

![k8s CI](https://github.com/fed4iot/VirIoT/workflows/k8s%20CI/badge.svg)
![docker CI](https://github.com/fed4iot/VirIoT/workflows/docker%20CI/badge.svg)
  
__These are the instructions to test the ThingVisor a local Docker-based VirIoT system
The setup has been tested on Ubuntu 18.04.__

# VirIoT platform setup (Docker)

## Activate python3 bash autocomplete  

This allows autocompleting commands of the Fed4IoT Command Line Interface (F4I) 

```bash  
sudo apt-get install python3-argcomplete
sudo activate-global-python-argcomplete3  
```

## Clone Git Repository

```bash  
git clone https://github.com/fed4iot/VirIoT.git
cd VirIoT  
```

## Run mosquitto MQTT server for Internal Information Sharing

```bash  
sudo service mosquitto start
```

## Run MongoDB system-database in a Docker container

```bash  
docker run -d --name mongo-container -p 32768:27017 mongo:3.4.18  
```  

If already run but stopped, use `docker start mongo-container`.
To reset the DB delete the container and run it again.  
To explore DB use `mongo-compass` and connect to the IP address of the container.

## Run Master-Controller

Change directory to `VirIoT/Master-Controller`.

Configure the right IP addresses and ports editing the settings template file `settings-docker-template.py` with your correct configurations and copy it to the `data` folder.
The default port of Master-Controller is the `8090` where it exposes the VirIoT REST API-.

```bash  
vim settings-docker-template.py  
# edinting.....then copy and rename it to data/settings.py  
cp settings-docker-template.py data/settings.py  
```

The file `db_setup.py` is used by `master-controller.py` for setting parameters, such as the password of the 'admin' user whose default value is 'passw0rd'. It is not necessary to change it unless to change the password. 

Install python3 dependencies

```bash
pip3 install -r requirements.txt
```

Run master-controller

```bash
python3 master-controller.py
```  

## Configure the `f4i` Command Line Interface  

Open new terminal and change directory to `VirIoT/CLI`

From here you can use `python3 f4i.py` and press tab for autocomplete, for help you can use `python3 f4i.py -h`.  Furthermore, you can use for example  `python3 f4i.py add-thingvisor -h` for sub-help. 
Next commands do not include some CLI options whose default values properly works for the local VirIoT Docker based deployment we are considering (e.g., -c 127.0.0.1:8090). for other deployments, e.g. on Kubernetes, additional options may be required, as explained by the command help.  
  
### Login  

Login as `admin`. Access control uses JWT (JSON Web Token).  
Latest access token stored in $HOME/.viriot/token and used for every interaction with the master controller.  

```bash  
python3 f4i.py login -u admin -p passw0rd 
```  

From now on you are allowed to execute any CLI command

# Test the ThingVisor

## Build the ThingVisor (optional)

The ThingVisor code is usually available on Fed4IoT DockerHub. To build it locally, open a new terminal and change directory to `VirIoT/Thingvisors/DockerThingVisor/FIWARE-flavoured-ThingVisors`

To build rpz image:

```bash
docker build -t fed4iot/fiware-rpz-tv -f buildImages/RPZ-TV/Dockerfile  ./
```

## Add the ThingVisor through the `f4i` Command Line Interface  

Use the terminal with the CLI and execute
  
```bash  
python3 f4i.py add-thingvisor -i fed4iot/fiware-rpz-tv -n thingVisorID_RPZ -d "thingVisorID_RPZ" -p '{"ocb_ip":"<OCB_Public_IP>", "ocb_port":"<OCB_Port>"}'
```  

JSON parameters are: 
- `ocb_ip`, `ocb_port`:  the public IP and port of the Orion Context Broker where recover RPZ information


## Connect the ThingVisor with Orion Context Broker

Check that the connection has been made by monitoring the status on the ThingVisor through the CLI

```bash  
python3 f4i.py list-thingvisors  
```

If ThingVisor is properly connected you should see `vThings` information in the command result like the following ones :

```json
[
    {
        "thingVisorID": "thingVisorID_RPZ",
        "status": "running",
        "yamlFiles": null,
        "creationTime": "****-**-**T**:**:**.******",
        "tvDescription": "thingVisorID_RPZ",
        "containerID": "66ba4e567f5d100c527c02f53a6fc39c191a4d5609fca9b2d91a8adbaf1a90c5",
        "imageName": "fed4iot/fiware-rpz-tv",
        "ipAddress": "172.17.0.3",
        "debug_mode": false,
        "vThings": [
            {
                "label": "Service:ora # ServicePath:/#",
                "id": "thingVisorID_RPZ/parkingmeter",
                "description": ""
            },
            {
                "label": "Service:ora # ServicePath:/#",
                "id": "thingVisorID_RPZ/policy",
                "description": ""
            },
            {
                "label": "Service:ora # ServicePath:/#",
                "id": "thingVisorID_RPZ/sector",
                "description": ""
            }
        ],
        "params": "{'ocb_ip':'<OCB_Public_IP>', 'ocb_port':'<OCB_Port>'}",
        "MQTTDataBroker": {
            "ip": "172.17.0.1",
            "port": 1883
        },
        "MQTTControlBroker": {
            "ip": "172.17.0.1",
            "port": 1883
        },
        "port": {
            "1030/tcp": "32950"
        },
        "IP": ""
    }
]

```

## Internal test

Open a new terminal, and make a subscription on the MQTT internal bridge to see any internal message exchange

```bash
mosquitto_sub -t "#" -v
```

## End to end tests with a ORION vSilo

This test shows how to receive information from Orion Context Broker (NGSIv2) of a provider in an ORION vSilo whose Docker image fed4iot/fiware-f is assumed available. The same test can be repeated for other vSilo flavours.

If fed4iot/fiware-f isn't available, you can build changing  directory to `VirIoT/Flavours/orion-flavour` and running:

```bash  
./build.sh
```

### Add the vSilo flavours

Move in a CLI terminal and execute

```bash  
python3 f4i.py add-flavour -f orion-f -s "" -i fed4iot/fiware-f -d "silo with a FIWARE Orion Context Broker"
```

### Create a vSilo, e.g. orion

```bash
python3 f4i.py create-vsilo -f orion-f -t tenant1 -s Silo1
```

Discover the vSilo local IP address (e.g. 172.17.0.4) and broker expose port  (port["1026/tcp"]) observing information obtained by:

```bash
python3 f4i.py list-vsilos
```

### Add the vThing parkingmeter one to the vSilo

```bash
python3 f4i.py add-vthing -v thingVisorID_RPZ/parkingmeter -t tenant1 -s Silo1
```

Now, you must find the message exchange on the MQTT broker monitor:

```bash
vThing/thingVisorID_RPZ/parkingmeter/c_in ; payload: {"command":"getContextRequest","vSiloID":"tenant1_Silo1","vThingID":"thingVisorID_RPZ/parkingmeter"}
vSilo/tenant1_Silo1/c_in {"command":"getContextResponse","data":[ ... ],"meta":{"vThingID":"thingVisorID_RPZ/parkingmeter"}}
```

Finally, if you are using Orion vSilo, you can access to vSilo Broker (Orion Context Broker) to recover RPZ information, using NGSIv2 API:

```bash
curl --location --request GET 'http://<vSiloPublicIP>:<vSiloBrokerExposePort>/v2/entities?limit=100&options=count' --header 'Accept: application/json'
```