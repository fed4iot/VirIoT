# License

ThingVisor source code files are made avaialable under the Apache License, Version 2.0 (Apache-2.0), located into the LICENSE file.

# README

This ThingVisor obtains regulated parking zones information (RPZ) from a FIWARE's Orion Context Broker (OCB) using NGSIv2 API.
The [Test.md](./Test.md) describe how to test the ThingVisor.

## How To Run

### Local Docker deployment

Use the VirIoT CLI as admin and run the following command, you must define OCB endpoint.

```bash  
python3 f4i.py add-thingvisor -i fed4iot/fiware-rpz-tv -n thingVisorID_RPZ -d "thingVisorID_RPZ" -p "{'ocb_ip':'<OCB_Public_IP>', 'ocb_port':'<OCB_Port>'}"
```

### Kubernetes deployment

Use the VirIoT CLI as admin and run the following command, you must define OCB endpoint.

```bash  
python3 f4i.py add-thingvisor -c http://[k8s_node_ip]:[NodePort] -n thingVisorID_RPZ -d "thingVisorID_RPZ" -p "{'ocb_ip':'<OCB_Public_IP>', 'ocb_port':'<OCB_Port>'}" -y "yaml/thingVisor-murcia-rpz.yaml"
```

## NGSI-LD data model

Each parkingmeter obtained from OCB is represented by an NGSI-LD entity like the following one:

```json
{
  "id":"urn:ngsi-ld:parkingmeter:Parquimetro:20",
  "type":"parkingmeter",
  "name":{
    "type":"Property",
    "value":"PUERTA%20NUEVA"
  },
  "location":{
      "type":"GeoProperty",
        "value":{
                "type":"Point",
                "coordinates":[-1.128053634,37.99128625]
                }
  },
  "@context":["https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld",
              "https://gitlab.com/Odins/fed4iot/contextfiles/-/blob/master/parkingmeter-context.jsonld"]  
}

```
