# OneM2M ThingVisor
This is a OneM2M ThingVisor which enables communications between the IoT devices through the OneM2M standard.

## How To Run

### Local Docker deployment

Use the [VirIoT CLI](../../../Doc/CLI%20Usage%20Example.md) and run the following command to run the ThingVisor example.
Please specify the Mobius server address as `CSEurl`, origin resource as `origin`, the list of Mobius subscriptions in `cntArns`, 
the `vThingName` and its `vThingDescription`. For better comprehension see the JSON structure below:
```json
{
	"CSEurl": "Mobius server address",
	"origin": "origin resource",
	"cntArns": "OneM2M subscription",
	"vThingName": "Name of the created vThing",
	"vThingDescription": "Description of the created vThing"
}
```

Finally, run the example command to run the OneM2M Multisub ThingVisor on Docker:
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