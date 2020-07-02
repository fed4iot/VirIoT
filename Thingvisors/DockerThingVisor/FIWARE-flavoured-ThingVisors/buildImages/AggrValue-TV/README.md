# License

ThingVisor source code files are made avaialable under the Apache License, Version 2.0 (Apache-2.0), located into the LICENSE file.

# README

This ThingVisor obtains an entity, which contains the sum of free spaces of parking sites (aggregated value) from a FIWARE's Orion Context Broker (OCB) using NGSIv2 API.
The [Test.md](./Test.md) describe how to test the ThingVisor.

## How To Run

### Local Docker deployment

Use the VirIoT CLI as admin and run the following command, you must define OCB endpoint.

```bash  
python3 f4i.py add-thingvisor -i fed4iot/fiware-aggrvalue-tv -n thingVisorID_AggrValue -d "thingVisorID_AggrValue" -p "{'ocb_ip':'<OCB_Public_IP>', 'ocb_port':'<OCB_Port>'}"
```

### Kubernetes deployment

Use the VirIoT CLI as admin and run the following command, you must define OCB endpoint.

```bash  
python3 f4i.py add-thingvisor -c http://[k8s_node_ip]:[NodePort] -n thingVisorID_AggrValue -d "thingVisorID_AggrValue" -p "{'ocb_ip':'<OCB_Public_IP>', 'ocb_port':'<OCB_Port>'}" -y "yaml/thingVisor-murcia-aggrvalue.yaml"
```

## NGSI-LD data model

Obtain an unique entity (NGSI-LD format) like the following one:

```json

{
    "id":"urn:ngsi-ld:parkingsite:vThingParkingSite",
    "type":"parkingsite",
    "totalFreeParkingSpaces":{
      "type":"Property",
      "value":440
    },
    "observedAt":{
      "type":"Property",
      "value":{
              "@type":"DateTime",
              "@value":"2020-05-21T13:53:19Z"
            }
    },
    "@context":["https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld",
                "https://gitlab.com/Odins/fed4iot/contextfiles/-/blob/master/parkingsite-context.jsonld"]
}
```
