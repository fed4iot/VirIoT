# Hello World ThingVisor

This is a dummy ThingVisor with the purpose of testing, that periodically sends data every 5 seconds.
The publication rate is specified at creation time but it's possible to update it through the 
[updateTV API](../../../Doc/CLI%20Usage%20Example.md#update-thingvisor). 

The HelloWorld ThingVisor exports one vThing named `hello` where it publishes data.

## How To Run

### Local Docker deployment

Use the VirIoT CLI and run the following command to run the ThingVisor example.

```bash
python3 f4i.py add-thingvisor -i fed4iot/helloworld-tv:latest -n helloworldtv -d "hello thingVisor"
```

### Kubernetes deployment

Use the VirIoT CLI and run the following command to run the ThingVisor example.  
The `-z` argument is optional, it can be used to specify the deployment zone. If not specified,   
Kubernetes will randomly choose a node in the default zone.

```bash
python3 f4i.py add-thingvisor -c http://[k8s_node_ip]:[NodePort] -n helloworldtv -d "hello thingVisor" -y "yaml/thingVisor-helloWorld.yaml"
```

## NGSI-LD data model
 
The NGSI-LD entity of the generic `HelloSensorX is the following:

```json
{
    "id": "urn:ngsi-ld:HelloSensorX",
    "type": "my-counter",
    "counter": {
        "type": "Property",
        "value": 313
    }
}
```
