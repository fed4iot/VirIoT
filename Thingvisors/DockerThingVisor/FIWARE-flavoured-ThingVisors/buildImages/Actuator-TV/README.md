# License

ThingVisor source code files are made avaialable under the Apache License, Version 2.0 (Apache-2.0), located into the LICENSE file.

# README

This ThingVisor obtains entities from a FIWARE's Orion Context Broker (OCB) using NGSIv2 API and supports performance over entities which have commands. It works both with a real provider environments and with the FiWARE Provider Simulator in the Extra folder. The [Test.md](./Test.md) describe how to test the ThingVisor.

## How To Run

### Local Docker deployment

Use the VirIoT CLI as admin and run the following command, you must define OCB endpoint.

```bash  
python3 f4i.py add-thingvisor -i fed4iot/fiware-actuator-tv -n thingVisorID_Actuator -d "thingVisorID_Actuator" -p '{"ocb_ip":"<OCB_Public_IP>", "ocb_port":"<OCB_Port>", "ocb_service":["<service>",...],"ocb_servicePath":["<servicePath>",...]}'
```

### Kubernetes deployment

Use the VirIoT CLI as admin and run the following command, you must define OCB endpoint.

```bash  
python3 f4i.py add-thingvisor -c http://[k8s_node_ip]:[NodePort] -n thingVisorID_Actuator -d "thingVisorID_Actuator" -p '{"ocb_ip":"<OCB_Public_IP>", "ocb_port":"<OCB_Port>", "ocb_service":["<service>",...],"ocb_servicePath":["<servicePath>",...]}' -y "yaml/thingVisor-fiWAREActuator.yaml"
```

## NGSI-LD data model

Each entity obtained from OCB is represented by an NGSI-LD entity, following the next schema:


```json
{
  "id":"<entity identifier>",
  "type":"<entity type>",
  "attribute1":{
    "type":"Property",
    "value":"property value"},
  ...
  "attributeN":{
    "type":"Property",
    "value":"property value"},
  //If entity has commands...
  "commands": {
    "type":"Property",
    "value":["<command1>",...]},
  "@context":["https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld"]

}

```

In a specific case:
```json

{
  "id":"urn:ngsi-ld:Device:001",
  "type":"Device",
  "TimeInstant":{
    "type":"Property",
    "value":"2020-06-04T10:14:18.102Z"},
  "isOpen":{
    "type":"Property",
    "value":"false",
    "TimeInstant":{
      "type":"Property",
      "value":"2020-06-04T10:14:18.093Z"}},
  "name":{
    "type":"Property",
    "value":"Device:001 provision",
    "TimeInstant":{
      "type":"Property",
      "value":"2020-06-04T10:14:18.102Z"}},
  "commands":{
    "type":"Property",
    "value":["start","stop"]},
  "@context":["https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld"]
}
```
