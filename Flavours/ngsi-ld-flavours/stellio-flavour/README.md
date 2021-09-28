# README

This flavour exposes vThing information in [NGSI-LD](https://www.etsi.org/deliver/etsi_gs/CIM/001_099/009/01.02.02_60/gs_CIM009v010202p.pdf) format, through the [Stellio](https://github.com/stellio-hub/stellio-context-broker) Context Broker. Stellio is an NGSI-LD compliant context broker developed by EGM.

NGSI-LD is an open API and Datamodel specification for context management published by ETSI.

This flavour is for developers that want to use the NGSI-LD datamodel, which is based on the concept of Property Graphs, for representing IoT and context data, and the associated API, to provide and consume IoT data.


## How To Run

### Local Docker deployment

The Stellio broker is only available with Kubernetes deployments of VirIoT    

### Kubernetes deployment

First (as admin) add a "stellio flavour" to the system. With Kubernetes deployment we add the flavour by pointing to a yaml file, using argument -y, instead of a Docker image. Use the VirIoT CLI as admin and run the following command  (use "f4i.py add-flavour --help" for CLI parameters).

```bash
python3 f4i.py add-flavour -c http://[k8s_node_ip]:[NodePort] -f ngsild-stellio-f -d "silo with a Stellio NGSI-LD broker" -s "" -y "yaml/flavours-ngsild-stellio.yaml"
```

To create a vSilo, as above, run the following command (use "f4i.py create-vsilo --help" for CLI parameters). You need to specify the Kubernetes IP and the NodePort to reach the Master Controller you have already deployed in the cluster.

```bash
python3 f4i.py create-vsilo -c http://[k8s_node_ip]:[NodePort] -f ngsild-stellio-f -t tenant1 -s Silo1  
```


## NGSI-LD Mapping
Since this vSilo is based on a NGSI-LD broker, the mapping between the internal format and the external broker format is a one-to-one mapping.
| NGSI-LD internal                   |    | NGSI-LD external                               |
|------------------------------------|----|------------------------------------------------|
| entity                             | -> | entity                                         |



This flavour does not (yet) support actuation and inserting commands.
