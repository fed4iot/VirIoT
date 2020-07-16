# ThingVisor Relay

This ThingVisor creates a vThing whose data are JSON objects from an external producer through HTTP `/notify` endpoint.

## How To Run

### Local Docker deployment

Use the VirIoT CLI and run the following command to run the ThingVisor. The name of the ThingVisor (relayTV), the vThingName (timestamp) and the vThingType (timestamp) can be customized.

```bash
python3 f4i.py add-thingvisor -i fed4iot/relay-tv -n relayTV -d "relay thingvisor in japan" -p "{'vThingName':'timestamp','vThingType':'timestamp'}"
```

### Kubernetes deployment

Use the VirIoT CLI and run the following command to run the ThingVisor example.  The name of the ThingVisor (relayTV), the vThingName (timestamp) and the vThingType (timestamp) can be customized.
The `-z` argument is optional, it can be used to specify the deployment zone. If not specified,
Kubernetes will randomly choose a node in the default zone.

```bash
python3 f4i.py add-thingvisor -c http://[k8s_node_ip]:[NodePort] -y ../yaml/thingVisor-relay.yaml -n relayTV -d "relay thingvisor in japan" -p "{'vThingName':'timestamp','vThingType':'timestamp'}"
```

## NGSI-LD data model
 
The NGSI-LD entity published by the vThing is the following:

```json
{
    "id": "urn:ngsi-ld:<ThingVisorName>:<vThingName>",
    "type": "<vThingType>",
    "msg": {
        "type": "Property",
        "value": <received JSON object>
    }
}
```
