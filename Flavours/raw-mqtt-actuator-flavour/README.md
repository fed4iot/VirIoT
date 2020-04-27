# README

This flavour expose vThing information through a MQTT [Mosquitto](https://mosquitto.org/) broker.

## How To Run

### Local Docker deployment

Use the VirIoT CLI as admin and run the following command  (use "f4i.py add-flavour --help" for CLI parameters).

```bash  
python3 f4i.py add-flavour -f Raw-base-actuator-f -s Raw -i fed4iot/raw-mqtt-actuator-flavour -d "silo with a MQTT broker"
```

To create a vSilo run the following command (use "f4i.py create-vsilo --help" for CLI parameters).

```bash  
python3 f4i.py create-vsilo -f Raw-base-actuator-f -t tenant1 -s Silo1
```

### Kubernetes deployment

Use the VirIoT CLI as admin and run the following command  (use "f4i.py add-flavour --help" for CLI parameters).

```bash  
python3 f4i.py add-flavour -c http://[k8s_node_ip]:[NodePort] -f Raw-base-actuator-f -s Raw -d "silo with a MQTT broker" -y "yaml/flavours-raw-mqtt-actuator.yaml"
```

To create a vSilo run the following command (use "f4i.py create-vsilo --help" for CLI parameters).

```bash  
python3 f4i.py create-vsilo -c http://[k8s_node_ip]:[NodePort] -f Raw-base-actuator-f -t tenant1 -s Silo1
```


## NGSI-LD Mapping

| NGSI-LD                            |    | vSilo MQTT Topic                     |
|------------------------------------|----|--------------------------------------|
| entity JSON-LD                     | -> | tenantID/vThingID/NGSI-LD-Entity-ID  |

Each received NGSI-LD Entity information is published on the topic tenantID/vThingID/NGSI-LD-Entity-ID, where tenantID is the identifier of the tenant, vThingID is the identifier of the vThing and NGSI-LD-Entity-ID is the id of the NGSI-LD entity.

To issue a command whose name is *cmd_name*, the user should connect with vSilo MQTT Topic and publish the cmd-request on the tenantID/vThingID/NGSI-LD-Entity-ID/*cmd_name* topic (see examples in the Philips Hue Actuator ThingVisor folder).
