# Hello World Actuator ThingVisor

This ThingVisor is a dummy ThingVisor showing basic actuator functionality. It exports only a vThing named Lamp01.

## How To Run

### Local Docker deployment

Use the VirIoT CLI and run the following command to run the ThingVisor actuator example.  

```bash
python3 f4i.py add-thingvisor -i fed4iot/helloworld-actuator-tv -n helloworldtv -d "hello thingvisor"
```

### Kubernetes deployment

Use the VirIoT CLI and run the following command to run the ThinghVisor actuator example.  
The `-z` argument is optional, it can be used to specify the deployment zone. If not specified,   
Kubernetes will randomly choose a node in the default zone.

```bash
python3 f4i.py add-thingvisor -c http://[k8s_node_ip]:[NodePort] -n helloworldtv -d "hello thingvisor" -y "yaml/thinghVisor-helloWorldActuator.yaml"
```


## NGSI-LD data model

The NGSI-LD entity of Lamp01 is the following:

```json
{
 "id": "urn:ngsi-ld:helloworldtv:Lamp01",
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
