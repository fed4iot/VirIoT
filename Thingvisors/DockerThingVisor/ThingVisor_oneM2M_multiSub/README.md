# OneM2M Multisub ThingVisor
This is a [OneM2M ThingVisor](../ThingVisor_oneM2M_copy/README.md) for multiple subscriptions.

## How To Run

### Local Docker deployment

Use the [VirIoT CLI](../../../Doc/CLI%20Usage%20Example.md) and run the following command to run the ThingVisor example.

You must set the OneM2M header user request "origin" as "Superman", specify the Mobius server address in "CSEurl", 
the list of "OneM2M container absolute resource name" in "cntArns", the "vThingName" and "vThingDescription".

In particular, this command runs a ThingVisor that is subscribed to the OneM2M server at "https://fed4iot.eglobalmark.com" 
for the "Abbas123456/humidity/value" and "Abbas123456/temperature/value" OneM2M containers and creates a vThing named "EGM-Abbas123456".

```bash
python3 f4i.py add-thingvisor -i fed4iot/onem2m-multisub-tv:2.2 -n EGM-Abbass-multiple -d "OneM2M data from EGM Abbass sensor (temperature and humidity" -p '{"CSEurl":"https://fed4iot.eglobalmark.com","origin":"Superman","cntArns":["Abbas123456/humidity/value","Abbas123456/temperature/value"],"vThingName":"EGM-Abbas123456","vThingDescription":"OneM2M data from multiple EGM Abbass sensors"}'
```

## NGSI-LD data model
Each vThing is internally represented by the following entities:

```json
[{
    "id": "urn:ngsi-ld:EGM-Abbas123456",
    "type": "humidity",
    "Abbas123456:humidity:value": {
      "type": "Property", 
      "value": 66
    }
},
{
    "id": "urn:ngsi-ld:EGM-Abbas123456",
    "type": "temperature",
    "Abbas123456:temperature:value": {
      "type": "Property", 
      "value": 288.19
    }
}]
```