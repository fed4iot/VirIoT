# FogFlow ThingVisor

This is a dummy ThingVisor with the purpose of testing, that periodically sends data every 5 seconds.
The publication rate is specified at creation time but it's possible to update it through the 
[updateTV API](../../../Doc/CLI%20Usage%20Example.md#update-thingvisor). 

The HelloWorld ThingVisor exports one vThing named `hello` where it publishes data.

## How To Run

### build the docker image of FogFlow ThingVisor 

```bash
./build
```

### start the fed4iot system

```bash
docker-compose -f fed4iot.yml up -d 
cd ../../Master-Controller
python3 master-controller.py
```

### start the FogFlow thingVisor

```bash
cd ./CLI
python3 f4i.py add-thingvisor -i fed4iot/fogflow-tv:latest -n fogflow -d "FogFlow thingVisor"
```

### update the FogFlow thingVisor

Update the FogFlow ThingVisor to start or stop a service topology
```bash
python3 f4i.py update-thingvisor -i fed4iot/fogflow-tv:latest -n fogflow -d "FogFlow thingVisor"  -p '{"service_topology": "test", "command": "start"}'
```

### stop the FogFlow thingVisor

```bash
cd ./CLI
python3 f4i.py del-thingvisor -i fed4iot/fogflow-tv:latest -n fogflow -d "FogFlow thingVisor"
```
