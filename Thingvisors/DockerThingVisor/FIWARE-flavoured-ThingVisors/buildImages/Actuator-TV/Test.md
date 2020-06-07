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

## Build the FiWARE Provider Simulator (optional)

Open a new terminal and change directory to `VirIoT/Extra/FiWARE-Provider-Simulator`

Run FiWARE Provider Simulator to test the ThingVisor with the simulator rather than a real FiWARE Provider one.

```bash  
./build.sh
docker-compose up -d
``` 

You can see mqtt comunications in provider side running:
```bash  
./mqtt-provider-monitor.sh
``` 

Finally, provision the mqtt devices, to create the corresponding entities in Orion Context Broker of the provider environment. To do it, change to provisioning-devices subfolder and run:

```bash  
./device001.sh
``` 
NOTE: To obtain more entities in Orion Context Broker of provider you can run device002.sh and device003.sh too.


Finally, you can access to Orion Context Broker of provider to recover entities information running:

```bash
./broker-provider-monitor.sh
```

## Build the ThingVisor (optional)

The ThingVisor code is usually available on Fed4IoT DockerHub. To build it locally, open a new terminal and change directory to `VirIoT/Thingvisors/DockerThingVisor/FIWARE-flavoured-ThingVisors`

To build actuator image:

```bash
docker build -t fed4iot/fiware-actuator-tv -f buildImages/Actuator-TV/Dockerfile  ./
```

## Add the ThingVisor through the `f4i` Command Line Interface  

Use the terminal with the CLI and execute
  
```bash  
python3 f4i.py add-thingvisor -i fed4iot/fiware-actuator-tv -n thingVisorID_Actuator -d "thingVisorID_Actuator" -p "{'ocb_ip':'<OCB_Public_IP>', 'ocb_port':'<OCB_Port>', 'ocb_service':['demo1'],'ocb_servicePath':['/demo']}"
```  

JSON parameters are: 
- `ocb_ip`, `ocb_port`:  the public IP and port of the Orion Context Broker where recover entities information
- `ocb_service`, `ocb_servicePath`:  the service and servicePath where recover entities information

NOTE: To obtain more entities (device002 and device003) in Orion Context Broker of provider if you define 'ocb_service':['demo1','demo2'],'ocb_servicePath':['/demo','/demo']

## Connect the ThingVisor with Orion Context Broker

Check that the connection has been made by monitoring the status on the ThingVisor through the CLI

```bash  
python3 f4i.py list-thingvisors  
```

If ThingVisor is properly connected you should see `vThings` information in the command result like the following ones :

```json
[
    {
        "IP": "",
        "MQTTControlBroker": {
            "ip": "172.17.0.1",
            "port": 1883
        },
        "MQTTDataBroker": {
            "ip": "172.17.0.1",
            "port": 1883
        },
        "containerID": "8ad9e49cf3b8a2d33a30f5192992ece5ee8fc90b1966566e2cfa1755c41c1699",
        "creationTime": "****-**-**T**:**:**.******",
        "debug_mode": false,
        "imageName": "fed4iot/fiware-actuator-tv",
        "ipAddress": "172.17.0.3",
        "params": "{'ocb_ip':'<OCB_Public_IP>', 'ocb_port':'<OCB_Port>', 'ocb_service':['demo1'],'ocb_servicePath':['/demo']}",
        "port": {
            "1030/tcp": "33220"
        },
        "status": "running",
        "thingVisorID": "thingVisorID_Actuator",
        "tvDescription": "thingVisorID_Actuator",
        "vThings": [
            {
                "description": "",
                "id": "thingVisorID_Actuator/Device0",
                "label": "Type:Device # Service:demo1 # ServicePath:/demo"
            }
        ],
        "yamlFiles": null
    }
]

```
NOTE: If you have more entities (device002 and device003) in Orion Context Broker you must have two elements in vThings array.

## Internal test

Internal test provides to inject in the internal MQTT broker neutral-format packets on the topics the ThingVisor is listening to in order to observe its behavior.

Example mqtt publications are in [Test/mqtt-commands subfolder](./Test/mqtt-commands). In this instance, we can run the [device001-start.sh](./Test/mqtt-commands/device001-start.sh) and [device001-stop.sh](./Test/mqtt-commands/device001-stop.sh) ones.


Open a new terminal, and make a subscription on the MQTT internal bridge to see any internal message exchange

```bash
mosquitto_sub -t "#" -v
```

Open a new terminal, change directory to `VirIoT/Thingvisors/DockerThingVisor/FIWARE-flavoured-ThingVisors/buildImages/Actuator-TV/Test/mqtt-commands`, and run:

```bash
./device001-start.sh
```
or
```bash
./device001-stop.sh
```

You should observe the following messages on the internal MQTT broker.

### command request

```bash
vThing/thingVisorID_Actuator/Device0/data_in {"meta":{"vSiloID":"tenant1_Silo1"},"data":[{"id":"urn:ngsi-ld:Device:001","type":"Device","start":{"type":"Property","value":{"cmd-value": "","cmd-qos":"0","cmd-id":"001","cmd-nuri":["viriot:vSilo/tenant1_Silo1/data_in"]}}}]}
```

### Provider property update

```bash
vThing/thingVisorID_Actuator/Device0/data_out {"data":[{"type":"Device","TimeInstant":{"type":"Property","value":"2020-06-04T13:28:44.639Z"},"isOpen":{"type":"Property","value":"true","TimeInstant":{"type":"Property","value":"2020-06-04T13:28:44.639Z"}},"name":{"type":"Property","value":"Device:001 provision","TimeInstant":{"type":"Property","value":"2020-06-04T13:28:44.639Z"}},"commands":{"type":"Property","value":["start","stop"]},"@context":["https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld"],"id":"urn:ngsi-ld:Device:001"}],"meta":{"vThingID":"thingVisorID_Actuator/Device0"}}
```

### command request & result

```bash
vSilo/tenant1_Silo1/data_in {"data":[{"id":"urn:ngsi-ld:Device:001","type":"Device","start-result":{"type":"Property","value":{"cmd-value":"","cmd-qos":"0","cmd-id":"001","cmd-nuri":["viriot:vSilo/tenant1_Silo1/data_in"],"cmd-result":"OK"},"TimeInstant":{"type":"Property","value":"2020-06-04T13:28:44.643Z"}},"start-status":{"type":"Property","value":{"cmd-value":"","cmd-qos":"0","cmd-id":"001","cmd-nuri":["viriot:vSilo/tenant1_Silo1/data_in"],"cmd-status":"OK"},"TimeInstant":{"type":"Property","value":"2020-06-04T13:28:44.643Z"}}}],"meta":{"vThingID":"thingVisorID_Actuator/Device0"}}

```

You should observe too the following messages on the MQTT provider broker.

### Provider mqtt monitor

```bash
...
/fed4iot/device001/attrs {"s":false}
/fed4iot/device001/cmd {"start":{"value":"","cmd-id":"2f298ddb-3eea-40d5-f9a1-c83741bf73f3"}}
/fed4iot/device001/attrs {"s":"true"}
/fed4iot/device001/cmdexe {"start":{"value":"","cmd-id":"2f298ddb-3eea-40d5-f9a1-c83741bf73f3"}}
...
```

## End to end tests with a ORION vSilo

This test shows how to send commands to a FiWARE provider environment (NGSIv2) through an ORION vSilo whose Docker image fed4iot/fiware-f is assumed available. The same test can be repeated for other vSilo flavours.

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

Discover the vSilo local IP address (e.g. 172.17.0.4) and broker exposed port (port["1026/tcp"]) observing information obtained by:

```bash
python3 f4i.py list-vsilos
```

### Add the vThing to the vSilo

```bash
python3 f4i.py add-vthing -v thingVisorID_Actuator/Device0 -t tenant1 -s Silo1
```

Now, you must find the message exchange on the MQTT broker monitor:

```bash
vThing/thingVisorID_Actuator/Device0/c_in {"command":"getContextRequest","vSiloID":"tenant1_Silo1","vThingID":"thingVisorID_Actuator/Device0"}
vSilo/tenant1_Silo1/c_in {"command":"getContextResponse","data":[{"type":"Device","TimeInstant":{"type":"Property","value":"2020-06-04T14:06:02.304Z"},"isOpen":{"type":"Property","value":"true","TimeInstant":{"type":"Property","value":"2020-06-04T14:06:02.304Z"}},"name":{"type":"Property","value":"Device:001 provision","TimeInstant":{"type":"Property","value":"2020-06-04T14:06:02.304Z"}},"commands":{"type":"Property","value":["start","stop"]},"@context":["https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld"],"id":"urn:ngsi-ld:Device:001"}],"meta":{"vThingID":"thingVisorID_Actuator/Device0"}}
```

Finally, if you are using Orion vSilo, you can access to vSilo Broker (Orion Context Broker) to recover entities information, you change to [Test subfolder](./Test) and run [broker-vSilo-monitor.sh](./Test/broker-vSilo-monitor.sh), to do it you need the broker exposed port of vSilo previously obtained:

```bash
./broker-vSilo-monitor.sh <broker-exposed-port-vSilo>
```

### Run the test

Before running the test, if you want to see all communications, you should be sure that the next terminals are visible and running:

- mqtt-provider-monitor.sh
- broker-provider-monitor.sh
- subscription on the MQTT internal bridge
- broker-vSilo-monitor.sh

Here we will explain how to deploy, in an easy way, a tenant simulator which sends commands to the vSilo broker and we will see how its attributes to update.

Open a new terminal, change directory to `VirIoT/Thingvisors/DockerThingVisor/FIWARE-flavoured-ThingVisors/buildImages/Actuator-TV/Test/tenantSimulator`. By default configuration, the docker-compose file is configured to deploy a unique tenant which starts and stops alternatively a device (device001). 

Configure the next docker-compose environment variables:
- `vSiloProtocol`, `vSiloHost`: the protocol and public IP of the vSilo Context Broker
- `vSiloPort`: <broker-exposed-port-vSilo>

and run:

```bash
./build.sh
docker-compose up
```

You should see how tenant sends commands and how these actions cause that `isOpen` attribute of device001 (vSilo broker) is changing (true/false).