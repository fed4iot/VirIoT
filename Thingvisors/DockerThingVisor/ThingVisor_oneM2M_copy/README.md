# OneM2M ThingVisor
This is a OneM2M ThingVisor which enables communications between the IoT devices through the OneM2M standard.

## How To Run

### Local Docker deployment

Use the VirIoT CLI and run the following command to run the ThingVisor example.

```bash
python3 f4i.py add-thingvisor -c http://[master_controller_ip]:[master_controller_port] -i fed4iot/onem2m-tv:2.2 -n EGM-Abbass -d "OneM2M data from EGM Abbass sensor" -p '{"CSEurl":"https://fed4iot.eglobalmark.com","origin":"Superman", "poaPort":"8089","cntArn":"Abbas123456/humidity/value","poaIP":"127.0.0.1","vThingName":"EGM-Abbas123456-humidity","vThingDescription":"OneM2M humidity data from EGM Abbass sensor"}'  
```

### Kubernetes deployment

Use the VirIoT CLI and run the following command to run the ThingVisor example.  
The `-z` argument is optional, it can be used to specify the deployment zone. If not specified,   
Kubernetes will randomly choose a node in the default zone.

```bash
python3 f4i.py add-thingvisor -c http://[k8s_node_ip]:[NodePort] -n EGM-Abbass -d "OneM2M data from EGM Abbass sensor" -p '{"CSEurl":"https://fed4iot.eglobalmark.com","origin":"Superman", "poaPort":"8089","cntArn":"Abbas123456/humidity/value","poaIP":"127.0.0.1","vThingName":"EGM-Abbas123456-humidity","vThingDescription":"OneM2M humidity data from EGM Abbass sensor"}' -y "../yaml/thingVisor-oneM2M.yaml" -z Japan  
```