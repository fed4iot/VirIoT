# README

The System vSilo is a special kind of virtual silo that is owned by the administrator of the VirIoT platform, and it contains all of the data produced by the platform, so as to make it accessible to external systems that may want to federate with VirIoT. The data is represented by using the ETSI standardized [NGSI-LD](https://www.etsi.org/deliver/etsi_gs/CIM/001_099/009/01.02.02_60/gs_CIM009v010202p.pdf) format, which is the internal "neutral" format used throughout VirIoT.
This System vSilo exposes information coming from vThing, in NGSI-LD format, through a prototype NGSI-LD Context Broker that implements a sub-set of the full NGSI-LD API specification, plus some additional features.

## How To Run

### Local Docker deployment

Currently, the System vSilo is only available when deploying VirIoT via Kubernetes.

### Kubernetes deployment

First (as admin) add a special "systemvsilo flavour" to the system, using the corresponding yaml file (-y command line argument). Use the VirIoT CLI as admin and run the following command (use "f4i.py add-flavour --help" for CLI parameters). The -s command line argument contains the custom parameters needed by this flavour. Specifically, the System vSilo needs to interact with the Master Controller with admin privileges, so we must specify the admin password and the endpoint to internally reach to the Master Controller.

```bash  
python3 f4i.py add-flavour -c http://[k8s_node_ip]:[NodePort] -f systemvsilo-f -d "System vSilo" -s '{"flavourtype":"systemvsilo", "adminpassword":"yourAdminPassword", "controllerurl":"http://f4i-master-controller-svc:8090"}' -y "../yaml/flavours-systemvsilo.yaml"
```
Then create a vSilo of that flavour, by running the following command (use "f4i.py create-vsilo --help" for CLI parameters).

```bash
python3 f4i.py create-vsilo -c http://[k8s_node_ip]:[NodePort] -t admin -f systemvsilo-f -s SystemSilo1
```
