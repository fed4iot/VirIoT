![k8s CI](https://github.com/fed4iot/VirIoT/workflows/k8s%20CI/badge.svg)
![docker CI](https://github.com/fed4iot/VirIoT/workflows/docker%20CI/badge.svg)
  
# Description

This ThingVisor is a dummy ThingVisor showing basic actuator functinality. It exports only a vThing named Lamp01.

# How To RUN (local Docker deployment)

Use the VirIoT CLI and run the follwiong command in case of a Hue Bridge whose IP address and port are 172.17.0.1:8080 (this is the case when using the emulator and a VirIoT Docker-base deployment)  

```bash  
python3 f4i.py add-thingvisor -i fed4iot/helloworld_actuator_tv -n helloWorldTV -d "hello thingvisor"
```

# NGSI-LD data model

The NGSI-LD entity of Lamp01 is the following:

```json
{
 "id": "urn:ngsi-ld:helloWorldTV:Lamp01",
 "type": "Lamp",
 "status": {
  "type": "Property",
  "value": "off"
 },
 "color": {
  "type": "Property",
  "value": "white"
 },
 "luminosity": {
  "type": "Property",
  "value": "255"
 },
 "commands": {
  "type": "Property",
  "value": ["set-color", "set-luminosity", "set-status"]
 }
}
```
