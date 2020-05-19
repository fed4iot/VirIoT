# OneM2M Multisub ThingVisor
This is a [OneM2M ThingVisor](../ThingVisor_oneM2M_copy/README.md) for multiple subscriptions.

## How To Run

### Local Docker deployment

Use the [VirIoT CLI](../../../Doc/CLI%20Usage%20Example.md) to run the following ThingVisor. 
Please specify the Mobius server address as `CSEurl`, origin resource as `origin`, the list of Mobius subscriptions in `cntArns`, 
the `vThingName` and its `vThingDescription`. For better comprehension see the JSON structure below:
```json
{
	"CSEurl": "Mobius server address",
	"origin": "origin resource",
	"cntArns": [
		"list of subscriptions"
	],
	"vThingName": "Name of the created vThing",
	"vThingDescription": "Description of the created vThing"
}
```

Finally, run the example command to run the OneM2M Multisub ThingVisor on Docker:
```bash
python3 f4i.py add-thingvisor -i fed4iot/onem2m-multisub-tv:2.2 -n EGM-Abbass-multiple -d "OneM2M data from EGM Abbass sensor (temperature and humidity" -p '{"CSEurl":"https://fed4iot.eglobalmark.com","origin":"Superman","cntArns":["Abbas123456/humidity/value","Abbas123456/temperature/value"],"vThingName":"EGM-Abbas123456","vThingDescription":"OneM2M data from multiple EGM Abbass sensors"}'
```
