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

## Hue Emulator (optional)

Open a new terminal and change directory to `VirIoT/Extra/Hue-Emulator`

Run Hue emulator to test the ThingVisor with the emulator rather than a real Hue system. Click on the Start button. The default port is 8000.

```bash
java -jar HueEmulator-v0.8.jar
```

![GitHub Logo](Screenshot_2.png)

## Build the ThingVisor (optional)

The ThingVisor code is usually available on Fed4IoT DockerHub. To build it locally, open a new terminal and change directory to `VirIoT/Thingvisors/DockerThingVisor/ThingVisor_Philips_Hue`

To debug with Microsoft VS code through SSH uncomment Debug sections in Dockerfile and start.sh and add the public key id_rsa.pub to the directory.

```bash
docker build -t fed4iot/phue-actuator-tv .
```

## Add the ThingVisor through the `f4i` Command Line Interface  

Use the terminal with the CLI and execute
  
```bash  
python3 f4i.py add-thingvisor -i fed4iot/phue-actuator-tv -n pHueActuator -d "pHue actuator" -p '{"bridgeIP":"172.17.0.1", "bridgePort":"8000"}'
```  

JSON parameters are: `bridgeIP`, the IP address of the bridge (172.17.0.1 for Hue Emulator), and `bridgePort`, the port of the bridge (e.g. 5000 for the emulator, 80 for a real Hue bridge)

## Connect the ThingVisor with the Philips Hue bridge

Press the *Bridge Button* either on the emulator or a real bridge to allow the ThingVisor to connect and wait few seconds.

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
        "containerID": "0c0209c37f775827f346b3cfa2c9b5181d905f28a04d7ed0444f90a8df799bb9",
        "creationTime": "2020-04-21T22:22:01.742340",
        "debug_mode": false,
        "imageName": "fed4iot/phue-actuator-tv",
        "ipAddress": "172.17.0.3",
        "params": "{'bridgeIP':'172.17.0.1', 'bridgePort':'8000'}",
        "port": {},
        "status": "running",
        "thingVisorID": "pHueActuator",
        "tvDescription": "pHue actuator",
        "vThings": [
            {
                "description": "Extended color light",
                "id": "pHueActuator/light1",
                "label": "Hue Lamp 1",
                "type": "actuator"
            },
            {
                "description": "Extended color light",
                "id": "pHueActuator/light2",
                "label": "Hue Lamp 2",
                "type": "actuator"
            },
            {
                "description": "Extended color light", 
                "id": "pHueActuator/light3",
                "label": "Hue Lamp 3",
                "type": "actuator"
            }
        ],
        "yamlsFile": null
    }
]

```

## Internal test

Internal test provides to inject in the internal MQTT broker neutral-format packets on the topics the ThingVisor is listening to in order to observe its behavior.

Example neutral-format packets are: [set-hue](./commandRequestHueNeutralFormat.json), [set-on](./commandRequestHueNeutralFormat.json), [raw-command](./commandRequestHueNeutralFormat.json)

Open a new terminal, and make a subscription on the MQTT internal bridge to see any internal message exchange

```bash
mosquitto_sub -t "#" -v
```

Open a new terminal, change directory to  `VirIoT/Thingvisors/DockerThingVisor/ThingVisor_Philips_Hue/Test`, and inject a set-hue command. Optionally, edit the JSON file to change the hue value to be set.  

```bash
mosquitto_pub -t "vThing/pHueActuator/light1/data_in" -f ./commandRequestHueNeutralFormat.json
```

You should see the change of the color of light1 and observe the following messages on the internal MQTT broker

### command request

```json
vThing/pHueActuator/light1/data_in {"data":[{"id": "urn:ngsi-ld:pHueActuator:light1","type": "Lamp","set-hue" : {"type": "Property","value": {"cmd-value":12000, "cmd-qos":"2", "cmd-id":"123456", "cmd-nuri":"viriot:/vSilo/tenant1_vSilo1/data_in"}}}],"meta": {}}
```

### command status

```json
vThing/pHueActuator/light1/data_out {"data": [{"id": "urn:ngsi-ld:pHueActuator:light1", "type": "Extended color light", "set-hue-status": {"type": "Property", "value": {"cmd-value": 12000, "cmd-qos": "2", "cmd-id": "123456", "cmd-nuri": "viriot:/vSilo/tenant1_vSilo1/data_in", "cmd-status": "PENDING"}}}], "meta": {"vThingID": "pHueActuator/light1"}}
```

### hue property update

```json
vThing/pHueActuator/light1/data_out {"data": [{"id": "urn:ngsi-ld:pHueActuator:light1", "type": "Extended color light", "hue": {"type": "Property", "value": 12000}}], "meta": {"vThingID": "pHueActuator/light1"}}
```

### command result

```json
vThing/pHueActuator/light1/data_out {"data": [{"id": "urn:ngsi-ld:pHueActuator:light1", "type": "Extended color light", "set-hue-result": {"type": "Property", "value": {"cmd-value": 12000, "cmd-qos": "2", "cmd-id": "123456", "cmd-nuri": "viriot:/vSilo/tenant1_vSilo1/data_in", "cmd-result": "OK"}}}], "meta": {"vThingID": "pHueActuator/light1"}}
```

## End to end tests with a MQTT vSilo
This test shows how to drive the pHue bridge through a MQTT Raw vSilo whose Docker image _fed4iot/mobius-pub-sub-flavour-actuator_ is assumed available. The same test can be repeated for other vSilo flavours

### Add the vSilo flavours
Move in a CLI terminal and execute

```bash  
python3 f4i.py add-flavour -f Raw-base-f -s Raw -i fed4iot/raw-mqtt-actuator-flavour -d "silo with a MQTT broker"
```

### Create a vSilo, e.g. MQTT Raw

```bash
f4i.py create-vsilo -f Raw-base-f -t tenant1 -s Silo1
```

Discover the vSilo local IP address (e.g. 172.17.0.4) observing information obtained by

```bash
f4i.py list-vsilos
```

### Add the vThing light1 one to the vSilo

```bash
f4i.py add-vthing -v pHueActuator/light1 -t tenant1 -s Silo1
```

### Run the test
Open a new terminal, change directory to  `VirIoT/Thingvisors/DockerThingVisor/ThingVisor_Philips_Hue/Test`

Open the file MQTT-vSilo-test.py and change the internal IP address with the vSilo local IP address (e.g. 172.17.0.4) 

```bash
./MQTT-vSilo-test.py
```

To observe the message exchange on the vSilo MQTT broker, open a new terminal and run

```bash
mosquitto_pub -t "vThing/pHueActuator/light1/data_in" -f ./commandRequestHueNeutralFormat.json
```
