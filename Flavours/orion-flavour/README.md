# License

Orion Flavour source code files are made avaialable under the Apache License, Version 2.0 (Apache-2.0), located into the LICENSE file.

# README

This flavour exposes vThing information through Orion Context broker (FIWARE platform) which offers a NGSIv2 API. For more details about this broker: https://fiware-orion.readthedocs.io/en/master/


## How To Run

### Local Docker deployment

Build orion-flavour image running:
```bash  
./build.sh
```

Use the VirIoT CLI as admin and run the following command  (use "f4i.py add-flavour --help" for CLI parameters).

```bash  
python3 f4i.py add-flavour -f orion-f -s "" -i fed4iot/fiware-f -d "silo with a FIWARE Orion Context Broker"
```

To create a vSilo run the following command (use "f4i.py create-vsilo --help" for CLI parameters).

```bash  
python3 f4i.py create-vsilo -f orion-f -t tenant1 -s Silo1
```

### Kubernetes deployment

Use the VirIoT CLI as admin and run the following command  (use "f4i.py add-flavour --help" for CLI parameters).

```bash  
python3 f4i.py add-flavour -c http://[k8s_node_ip]:[NodePort] -f orion-f -s "" -d "silo with a FIWARE Orion Context Broker" -y "yaml/flavours-orion.yaml"
```

To create a vSilo run the following command (use "f4i.py create-vsilo --help" for CLI parameters).

```bash
python3 f4i.py create-vsilo -c http://[k8s_node_ip]:[NodePort] -f orion-f -t tenant1 -s Silo1  
```


## NGSI-LD Mapping

| NGSI-LD                            |    | NGSIv2                                                  |
|------------------------------------|----|---------------------------------------------------------|
| entity                             | -> | entity                                                  |
| entity id                          | -> | entity id                                               |
| entity type                        | -> | entity type                                             |
| property/relationship              | -> | attribute                                               |
| property/relationship name         | -> | attribute's name                                        |
| property/relationship type         | -> | attribute's type                                        |
| property value/relationship object | -> | attribute's value                                       |
| sub-property/sub-relationship      | -> | metadata                                                |

A vThing isn't represented inside Orion Context Broker (OCB).

An NGSI-LD entity, handled by the vThing, is represented as an entity in OCB. In NGSIv2 representation, entities keep the same 'id' and 'type' from NGSI-LD one.

A Property/Relationship of an NGSI-LD entity is represented as an attribute in NGSIv2 keeping the 'name' and 'value' and obtaining the corresponding type through value's data type.

Additional properties/relationship are considered metadata in NGSIv2.

The NGSI-LD property named `commands` is considered as a special case. This property contains an array with all the commands the entity supports. This property doesn't create an attribute `commands` in NGSIv2 entity. But three NGSIv2 attributes are created by each element of the array (<commands[i]>, <command[i]-result> and <commands[i]-status>.