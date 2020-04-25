![k8s CI](https://github.com/fed4iot/VirIoT/workflows/k8s%20CI/badge.svg)
![docker CI](https://github.com/fed4iot/VirIoT/workflows/docker%20CI/badge.svg)
  
# Description

This ThingVisor controls the lights connected to a Philips Hue bridge. It works both with a real bridge and with the Hue emularor (<https://steveyo.github.io/Hue-Emulator)> in the Extra folder.

# How To RUN (local Docker deployment)
Use the VirIoT CLI and run the follwiong command in case of a Hue Bridge whose IP address and port are 172.17.0.1:8080 (this is the case when using the emulator and a VirIoT Docker-base deployment)  

```bash  
python3 f4i.py add-thingvisor -i fed4iot/phue-actuator -n pHueActuator -d "pHue actuator" -p "{'bridgeIP':'172.17.0.1', 'bridgePort':'8000'}"
```

# NGSI-LD data model

Each light connected to the Philips bridge is represented by a NGSI-LD entity as the following for light1:

```json
{
 "id": "urn:ngsi-ld:pHueActuator:light1",
 "type": "Extended color light",
 "brightness": {
  "type": "Property",
  "value": 254
 },
 "saturation": {
  "type": "Property",
  "value": 254
 },
 "hue": {
  "type": "Property",
  "value": 4444
 },
 "on": {
  "type": "Property",
  "value": true
 },
 "commands": {
  "type": "Property",
  "value": ["set-brightness", "set-saturation", "set-hue", "set-on", "raw-command"]
 }
}
```
