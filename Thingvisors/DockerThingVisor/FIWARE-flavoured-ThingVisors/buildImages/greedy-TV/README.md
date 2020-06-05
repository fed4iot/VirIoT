# License

ThingVisor source code files are made avaialable under the Apache License, Version 2.0 (Apache-2.0), located into the LICENSE file.

# README

This ThingVisor obtains various information from a FIWARE Orion Context Broker (OCB) using the NGSIv2 API. To do it only is needed to specify all "Fiware-Services" that want to be considered.
The [Test.md](./Test.md) describe how to test the ThingVisor.

## How To Run

### Local Docker deployment

Use the VirIoT CLI as admin and run the following command, you must define OCB endpoint.

In this case, ThingVisor is configured to recover all entities from the next Fiware-Services: bicis, aparcamiento and ora.

```bash  
python3 f4i.py add-thingvisor -i fed4iot/fiware-greedy-tv -n thingVisorID_Greedy -d "thingVisorID_Greedy" -p "{'ocb_ip':'<OCB_Public_IP>', 'ocb_port':'<OCB_Port>','ocb_service':['<service',...]}"
```

### Kubernetes deployment

Use the VirIoT CLI as admin and run the following command, you must define OCB endpoint.

```bash  
python3 f4i.py add-thingvisor -c http://[k8s_node_ip]:[NodePort] -n thingVisorID_Greedy -d "thingVisorID_Greedy" -p "{'ocb_ip':'<OCB_Public_IP>', 'ocb_port':'<OCB_Port>','ocb_service':['<service>',...]}" -y "yaml/thingVisor-fiWARE.yaml"
```

## NGSI-LD data model

Each entity obtained from OCB is represented by an NGSI-LD entity, in the case of bicis' service, will obtain entities like the following one:

```json
{
    "id":"urn:ngsi-ld:Sensor:AparcamientoBicis:182",
    "type":"Sensor",
    "descripcion":{
      "type":"Property",
      "value":"Ronda00000000000000000021e00000000000000002020aray"},
    "geoposicion":{
        "type":"GeoProperty",
        "value":{
                  "type":"Point",
                  "coordinates":[-1.123326,37.985345]
                },
        "location":{
                      "type":"Property",
                      "value":"WGS84"
                  }
    },
    "habilitado":{
        "type":"Property",
        "value":"1"
    },
    "libres":{
      "type":"Property",
      "value":"16"
    },
    "ocupados":{
      "type":"Property",
      "value":"4"
    },
    "@context":["https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld"]
}

```
