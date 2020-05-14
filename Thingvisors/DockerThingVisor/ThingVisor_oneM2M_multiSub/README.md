# OneM2M ThingVisor
This is a [OneM2M ThingVisor](../ThingVisor_oneM2M_copy/README.md) for multiple subscriptions.

## How To Run

### Local Docker deployment

Use the VirIoT CLI and run the following command to run the ThingVisor example.

```bash
python3 f4i.py add-thingvisor -c http://[master_controller_ip]:[master_controller_port] -i fed4iot/onem2m-multisub-tv:2.2 -n EGM-Abbass-multiple -d "OneM2M data from EGM Abbass sensor (temperature and humidity" -p '{"CSEurl":"https://fed4iot.eglobalmark.com","origin":"Superman", "poaPort":"8089","cntArns":["Abbas123456/humidity/value","Abbas123456/temperature/value"],"poaIP":"127.0.0.1","vThingName":"EGM-Abbas123456","vThingDescription":"OneM2M data from multiple EGM Abbass sensors"}'
```