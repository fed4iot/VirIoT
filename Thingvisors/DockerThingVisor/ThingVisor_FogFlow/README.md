# FogFlow ThingVisor

The FogFlow-based ThingVisor 

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

### add the FogFlow thingVisor

```bash
python3 f4i.py add-thingvisor -c http://127.0.0.1:8090 -i fed4iot/fogflow-tv:latest -n fogflow -d "FogFlow thingVisor"
```

### list the thingVisor

```bash
python3 f4i.py list-thingvisors -c http://127.0.0.1:8090 
```

### update the FogFlow thingVisor

Update the FogFlow ThingVisor to start or stop a service topology
```bash
python3 f4i.py update-thingvisor -i fed4iot/fogflow-tv:latest -n fogflow -d "FogFlow thingVisor"  -p '{"service_topology": "test", "command": "start"}'
```

### delete the FogFlow thingVisor

```bash
python3 f4i.py del-thingvisor -c http://127.0.0.1:8090 -n fogflow 
```
