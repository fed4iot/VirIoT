# OneM2M ThingVisor
This is a OneM2M ThingVisor which enables communications between the IoT devices through the OneM2M standard.

## How To Run

### Local Docker deployment

Use the [VirIoT CLI](../../../Doc/CLI%20Usage%20Example.md) and run the following command to run the ThingVisor example.

You must set the OneM2M header user request "origin" as "Superman", specify the Mobius server address in "CSEurl", 
the "OneM2M container absolute resource name" in "cntArn", the "vThingName" and "vThingDescription".

In particular, this command runs a ThingVisor that is subscribed to the OneM2M server at "https://fed4iot.eglobalmark.com" 
for the "Abbas123456/humidity/value" OneM2M container and creates a vThing named "EGM-Abbas123456-humidity".

```bash
python3 f4i.py add-thingvisor -i fed4iot/onem2m-tv:2.2 -n EGM-Abbass -d "OneM2M data from EGM Abbass sensor" -p '{"CSEurl":"https://fed4iot.eglobalmark.com","origin":"Superman","cntArn":"Abbas123456/humidity/value","vThingName":"EGM-Abbas123456-humidity","vThingDescription":"OneM2M humidity data from EGM Abbass sensor"}'  
```

### Kubernetes deployment

Use the [VirIoT CLI](../../../Doc/CLI%20Usage%20Example.md) and run the following command to run the ThingVisor example.  
The `-z` argument is optional, it can be used to specify the deployment zone. If not specified,   
Kubernetes will randomly choose a node in the default zone.

```bash
python3 f4i.py add-thingvisor -c http://[k8s_node_ip]:[NodePort] -n EGM-Abbass -d "OneM2M data from EGM Abbass sensor" -p '{"CSEurl":"https://fed4iot.eglobalmark.com","origin":"Superman","cntArn":"Abbas123456/humidity/value","vThingName":"EGM-Abbas123456-humidity","vThingDescription":"OneM2M humidity data from EGM Abbass sensor"}' -y "../yaml/thingVisor-oneM2M.yaml" -z Japan  
```

## NGSI-LD data model
Each vThing is internally represented by the following entities:

```json
{
    "id": "urn:ngsi-ld:EGM-Abbas123456-humidity",
    "type": "humidity",
    "Abbas123456:humidity:value": {
      "type": "Property", 
      "value": 66
    }
}
```