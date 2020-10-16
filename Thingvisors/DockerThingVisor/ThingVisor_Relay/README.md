# ThingVisor Relay

This ThingVisor creates a vThing whose data are JSON objects received from an external producer through the HTTP `/notify` endpoint.

## How To Run

### Local Docker deployment

Use the VirIoT CLI and run the following command to run the ThingVisor. The name of the ThingVisor (relay-tv), the vThingName (timestamp) and the vThingType (timestamp) can be customized.

```bash
python3 f4i.py add-thingvisor -i fed4iot/relay-tv -n relay-tv -d "relay thingvisor in japan" -p "{'vThingName':'timestamp','vThingType':'timestamp'}"
```

### Kubernetes deployment

Use the VirIoT CLI and run the following command to run the ThingVisor example.  The name of the ThingVisor (relay-tv), the vThingName (timestamp) and the vThingType (timestamp) can be customized.

```bash
python3 f4i.py add-thingvisor -c http://[k8s_node_ip]:[NodePort] -y ../yaml/thingVisor-relay-http.yaml -n relay-tv -d "relay thingvisor with http" -p "{'vThingName':'timestamp','vThingType':'timestamp'}"
```

### Data injection
Linux curl can be used to push a JSON object as in the following example

```bash
curl -d '{"timestamp": 1594982023328, "sqn": 66941}' -H "Content-Type: application/json" -X POST http://<ThingVisorIP:ThingVisorPort>/notify
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
