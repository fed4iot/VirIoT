# Philips Hue ThingVisor

This ThingVisor controls the lights connected to a Philips Hue bridge. It works both with a real bridge and with the Hue emulator (<https://steveyo.github.io/Hue-Emulator)> in the [Extra](../../../Extra) folder.
The [Test.md](./Test.md) describe how to test the ThingVisor.

## How To Run

### Local Docker deployment

Use the VirIoT CLI and run the following command in case of a Hue Bridge whose IP address and port are 172.17.0.1:8080 (this is the case when using the emulator and a VirIoT Docker-base deployment).  

```bash
python3 f4i.py add-thingvisor -i fed4iot/phue-actuator-tv -n phueactuator -d "pHue actuator" -p "{'bridgeIP':'172.17.0.1', 'bridgePort':'8000'}"
```

### Kubernetes deployment

Use the VirIoT CLI and run the following command in case of a Hue Bridge whose IP address and port are 172.17.0.1:8080 (this is the case when using the emulator and a VirIoT k8s-base deployment).

```bash
python3 f4i.py add-thingvisor -c http://[k8s_node_ip]:[NodePort] -n phueactuator -d "pHue actuator" -p "{'bridgeIP':'172.17.0.1', 'bridgePort':'8000'}" -y "yaml/thingVisor-Philips-Hue.yaml"
```

## NGSI-LD data model

Each light connected to the Philips bridge is represented by a NGSI-LD entity as the following for light1:

```json
{
 "id": "urn:ngsi-ld:phueactuator:light1",
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
