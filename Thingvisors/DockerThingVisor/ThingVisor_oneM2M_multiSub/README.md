# OneM2M Multisub ThingVisor
This ThingVisor fetches content instances from a set of oneM2M containers within a oneM2M [Mobius](https://github.com/IoTKETI/Mobius) server. The ThingVisor exposes a single vThing, many NGSI-LD entities, and publishes latest container content instances as updates of NGSI-LD properties: one entity/property per container. Low latency is achieved by using oneM2M HTTP subscription functionality, therefore the ThingVisor should run on a device with a public IP address where to receive related notifications. The ThingVisor will automatically configure this networking aspect discovering system information.

## How To Run

### Local Docker deployment

Use the [VirIoT CLI](../../../Doc/CLI%20Usage%20Example.md) to run the ThingVisor. The oneM2M paramenters such as the `origin` of the request, the `CSEurl` (IP:port) of the Server, the list of containers (`cntArns`) absolute resource names, the `vThingName` and `vThingDescription` are passed as CLI parameters (-p). 
For instance, next CLI command runs a ThingVisor connected to the OneM2M server at "https://fed4iot.eglobalmark.com" and fetchs data items from  
the "Abbas123456/humidity/value" and "Abbas123456/temperature/value" oneM2M containers and creates a vThing named "EGM-Abbas123456". The related oneM2M applicatin entity (AE) is "Abbas123456"

```bash
python3 f4i.py add-thingvisor -i fed4iot/onem2m-multisub-tv:latest -n egm-abbass-multiple -d "OneM2M data from EGM Abbass sensor (temperature and humidity)" -p '{"CSEurl":"https://fed4iot.eglobalmark.com","origin":"Superman","cntArns":["Abbas123456/humidity/value","Abbas123456/temperature/value"],"vThingName":"EGM-Abbas123456","vThingDescription":"OneM2M data from multiple EGM Abbass sensors"}'
```

## NGSI-LD data model
The vThing of the ThingVisor internally publishes a NGSI-LD entity whose name is equal to the `vThingName`. When a content instance is created in a container, a NGSI-LD neutral-formt packet is internally published. The packet contains a NGSI-LD entity whose ID is equal to `urn:ngsi-ld:vThingName:cntArn` (with ":" instead of "/"). The NGSI-LD `type` is equal to the oneM2M name. The entity has a single property, whose name is equal to the  cntArn (with ":" instead of "/") and whose value contains the latest content instance as JSON.


```json
[{
    "id": "urn:ngsi-ld:egm-abbas123456:Abbas123456:humidity:value",
    "type": "Abbas123456",
    "Abbas123456:humidity:value": {
      "type": "Property", 
      "value": 66
    }
},
{
    "id": "urn:ngsi-ld:EGM-Abbas123456:Abbas123456:temperature:value",
    "type": "Abbas123456",
    "Abbas123456:temperature:value": {
      "type": "Property", 
      "value": 288.19
    }
}]
```