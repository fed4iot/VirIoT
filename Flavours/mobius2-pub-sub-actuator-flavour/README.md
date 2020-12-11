# README

This flavour expose vThing information through oneM2M [Mobius2](https://github.com/IoTKETI/Mobius) broker.

## How To Run

### Local Docker deployment

Use the VirIoT CLI as admin and run the following command  (use "f4i.py add-flavour --help" for CLI parameters).

```bash  
python3 f4i.py add-flavour -f Mobius2-base-actuator-f -s Mobius -i fed4iot/mobius2-pub-sub-actuator-flavour -d "silo with a oneM2M Mobius2 broker"
```

To create a vSilo run the following command (use "f4i.py create-vsilo --help" for CLI parameters).

```bash  
python3 f4i.py create-vsilo -f Mobius2-base-actuator-f -t tenant1 -s Silo1
```

### Kubernetes deployment

Use the VirIoT CLI as admin and run the following command  (use "f4i.py add-flavour --help" for CLI parameters).

```bash  
python3 f4i.py add-flavour -c http://[k8s_node_ip]:[NodePort] -f Mobius2-base-actuator-f -s Mobius -d "silo with a oneM2M Mobius2 broker" -y "yaml/flavours-mobius2-pub-sub-actuator.yaml"
```

To create a vSilo run the following command (use "f4i.py create-vsilo --help" for CLI parameters).

```bash
python3 f4i.py create-vsilo -c http://[k8s_node_ip]:[NodePort] -f Mobius2-base-actuator-f -t tenant1 -s Silo1  
```


## NGSI-LD Mapping

| NGSI-LD                            |    | oneM2M                                                  |
|------------------------------------|----|---------------------------------------------------------|
|                                    |    | AE resource name equal to vThingID                      |
| entity                             | -> | top-level container                                     |
| entity id                          | -> | top-level container resource name                       |
| entity type                        | -> | top-level container labels                              |
| property/relationship              | -> | sub-container                                           |
| property/relationship name         | -> | sub-container resource name                             |
| property/relationship type         | -> | sub-container labels                                    |
| property value/relationship object | -> | content instance of the sub-container                   |
| sub-property/sub-relationship      | -> | sub-sub-container (container nested with sub-container) |

A vThing is represented as a oneM2M Application Entity (AE) whose name is the VirIoT vThingID.

A NGSI-LD entity handled by the vThing is represented as a oneM2M *top-level* container of the AE whose resource name is the 'entity id'. The 'type' of the entity is inserted in the oneM2M 'label' of the top-level container.

A Property of a NGSI-LD Entity is represented as a oneM2M *sub* container of the top-level container whose resource name is the Property 'name'.

The 'value' of the Property is inserted as a oneM2M content instance in the sub container.

To issue a command whose name is *cmd_name*, the user should insert the cmd-request as content instance inside the *cmd_name* sub-container (see examples in the Philips Hue Actuator ThingVisor folder).
