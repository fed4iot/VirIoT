# Command Line Interface  

After the initial configuration, it is possible to interact with the VirIoT platform using the Command Line Interface (CLI) or Postman, provided the correct IP and port of the Master Controller are used.

## Postman
To interact with VirIoT platform using Postman, import the collection from the [Postman directory](../Postman)

## Use the CLI
To activate python3 and bash autocomplete:  

```bash  
sudo apt-get install python3-argcomplete   
sudo activate-global-python-argcomplete3  
```  
Now you can use `python3 f4i.py` and press tab for autocomplete, for help you can use `python3 f4i.py -h`.  
Furthermore, you can use for example  `python3 f4i.py create-vsilo -h` for sub-help.  

Also, it is required to install the `PyYAML` module, as follows:
```bash
pip3 install PyYAML
```

Move to the CLI directory to use the Command Line Interface.   
  
```bash  
cd VirIoT/CLI  
```  

IMPORTANT: The `f4i.py` CLI commands are the same for both the [Kubernetes-based](Kubernetes%20Deployment.md) 
and the [Docker-based](Docker%20Depolyment.md) deployments, provided of course you adjust `-c <ControllerURL>` argument, so that it points to the correct Master Conteroller's exposed IP and port.

When the commands differ, we show examples of both syntaxes. Usually, this is the case when they differ by usage of -y argument in Kubernets-based deployments, rather than -i argument, for instance in the Add Flavour action.

Concerning how to obtain the IP address of the Master-Controller, when running on Kubernetes, you can issue the following command; in this case, the most common possibilities for the `ControllerURL` are:
1. The ip address of the ClusterIP of the Master-Controller service along with the `8090` port.
2. The ip address of any node of the cluster, along with the `NodePort` of the Master-Controller service.
3. If set, the external ip address of any node of the cluster, followed by the `NodePort` of the Master-Controller service.

On Kubernetes, the following command is also very useful:
```bash  
# to know the ClusterIP and NodePort related to the Master-Controller service:  
kubectl get svc f4i-master-controller-svc 
```


### Login  
Login as `admin`. Access control uses JWT (JSON Web Token).  
Latest access token stored in `$HOME/.viriot/token` and used for every interaction with the Master-Controller.  

```bash  
python3 f4i.py login -c http://[master_controller_ip]:[master_controller_port] -u admin -p passw0rd  
```  
  

### Register  

As `admin` register user `tenant1` with password `password` and role `user`.

```bash  
python3 f4i.py register -c http://[master_controller_ip]:[master_controller_port] -u tenant1 -p password -r user  
```  
  

### Add Flavour  
There are already several vSilo Flavours available. For each command, forst the Docker-based variant is given, and then the Kubernetes-based variant (essentially they differ by usage of -y argument in Kubernets-based deployments, rather than -i argument. All other arguments are the same). (When using kubernetes, the yaml files of the various flavours are available in the "yaml" folder, they have the flavours-* prefix). 

#### MOBIUS (for developers that want to use the oneM2M IoT standard)
Add a vSilo flavour for [Mobius](https://github.com/IoTKETI/Mobius).
Mobius is a [oneM2M](http://www.onem2m.org) server implementation.
It got the oneM2M certification and it is designated as one of the golden samples.

```bash
# Docker: point to the docker image of the flavour using argument -i
python3 f4i.py add-flavour -c http://[master_controller_ip]:[master_controller_port] -i fed4iot/mobius-base-f:2.2 -f Mobius-base-f -s Mobius -d "silo with a oneM2M Mobius broker"  
# Kubernetes: point to the yaml file of the flavour using argument -y   
python3 f4i.py add-flavour -c http://[k8s_node_ip]:[NodePort] -y "../yaml/flavours-mobius-base.yaml" -f Mobius-base-f -s Mobius -d "silo with a oneM2M Mobius broker"  
```  


#### ORION (for developers that want to use the FIWARE NGSIv2 IoT standard)
Add a vSilo flavour for [Orion](https://fiware-orion.readthedocs.io/en/master/).
Orion is a C++ implementation of the [NGSIv2](https://fiware.github.io/specifications/ngsiv2/stable/) REST API
binding developed as a part of the FIWARE platform.

```bash
# Docker: point to the docker image of the flavour using argument -i 
python3 f4i.py add-flavour -c http://[master_controller_ip]:[master_controller_port] -i fed4iot/orion-f:2.2 -f orion-f -s "" -d "silo with a FIWARE Orion broker" 
# Kubernetes: point to the yaml file of the flavour using argument -y   
python3 f4i.py add-flavour -c http://[k8s_node_ip]:[NodePort] -y "../yaml/flavours-orion.yaml" -f orion-f -s "" -d "silo with a FIWARE Orion broker"
```  

#### SCORPIO (for developers that want to use the ETSI NGSI-LD standard for IoT and context data)
Add a vSilo flavour for [Scorpio](https://github.com/ScorpioBroker/ScorpioBroker).
Scorpio is an [NGSI-LD](https://www.etsi.org/deliver/etsi_gs/CIM/001_099/009/01.03.01_60/gs_CIM009v010301p.pdf)
compliant context broker developed by NEC Laboratories Europe and NEC Technologies India.
NGSI-LD is an open API and Datamodel specification for context management published by ETSI.
Scorpio is developed in Java using the SpringCloud microservices framework.

```bash
# Docker: point to the docker image of the flavour using argument -i 
python3 f4i.py add-flavour -c http://[master_controller_ip]:[master_controller_port] -i fed4iot/ngsild-scorpio-f:2.2 -f ngsild-scorpio-f -d "silo with a Scorpio NGSI-LD broker" -s ""  
# Kubernetes: point to the yaml file of the flavour using argument -y
python3 f4i.py add-flavour -c http://[k8s_node_ip]:[NodePort] -y "../yaml/flavours-ngsild-scorpio-multicontainer.yaml" -f ngsild-scorpio-f -d "silo with a Scorpio NGSI-LD broker" -s '{"brokerport":9090}'
```


#### STELLIO (for developers that want to use the ETSI NGSI-LD standard for IoT and context data)
Add a vSilo flavour for [Stellio](https://github.com/stellio-hub/stellio-context-broker).
Stellio is an [NGSI-LD](https://www.etsi.org/deliver/etsi_gs/CIM/001_099/009/01.03.01_60/gs_CIM009v010301p.pdf)
compliant context broker developed by EGM.
NGSI-LD is an open API and Datamodel specification for context management published by ETSI.
This project is part of FIWARE. For more information check the FIWARE Catalogue entry for Core Context.

```bash
# Docker: the STELLIO broker is only available with Kubernetes deployments of VirIoT
# Kubernetes: point to the yaml file of the flavour using argument -y
python3 f4i.py add-flavour -c http://[k8s_node_ip]:[NodePort] -y "../yaml/flavours-ngsild-stellio.yaml" -f ngsild-stellio-f -d "silo with a Stellio NGSI-LD broker" -s '{"brokerport":8090}'   
```  

#### ORIONLD (for developers that want to use the ETSI NGSI-LD standard for IoT and context data)
Add a vSilo flavour for [OrionLD](https://github.com/FIWARE/context.Orion-LD).
OrionLD is an [NGSI-LD](https://www.etsi.org/deliver/etsi_gs/CIM/001_099/009/01.03.01_60/gs_CIM009v010301p.pdf)
compliant context broker developed by FIWARE.
NGSI-LD is an open API and Datamodel specification for context management published by ETSI.
This Generic Enabler implements the NGSI-LD API Orion-LD extends the Orion Context Broker
This project is part of FIWARE. For more information check the FIWARE Catalogue entry for Core Context.

```bash
# Docker: the STELLIO broker is only available with Kubernetes deployments of VirIoT
# Kubernetes: point to the yaml file of the flavour using argument -y 
python3 f4i.py add-flavour -c http://[k8s_node_ip]:[NodePort] -y "../yaml/flavours-ngsild-orionld-multicontainer.yaml" -f ngsild-orionld-f -d "silo with a OrionLD NGSI-LD broker" -s '{"brokerport":1026}'  
```  



#### RAW MQTT
Add a vSilo flavour for exporting your raw IoT data to MQTT topics.

```bash  
python3 f4i.py add-flavour -c http://[master_controller_ip]:[master_controller_port] -f mqtt-f -i fed4iot/raw-mqtt-f:2.2 -d "silo with a Mosquitto broker" -s ""  
# Kubernetes: add the flavour yaml argument using -y   
python3 f4i.py add-flavour -c http://[k8s_node_ip]:[NodePort] -f mqtt-f -d "silo with a Mosquitto broker" -s "" -y "../yaml/flavours-raw-mqtt.yaml"  
```  
  

### List flavours  

```bash
# Docker
python3 f4i.py list-flavours -c http://[master_controller_ip]:[master_controller_port]  
# Kubernetes  
python3 f4i.py list-flavours -c http://[k8s_node_ip]:[NodePort]  
```  
  

### Add ThingVisor  

Add ThingVisor v-weather with some cities, for the Docker deployment. 
  
```bash  
python3 f4i.py add-thingvisor -c http://[master_controller_ip]:[master_controller_port] -i fed4iot/v-weather-tv:2.2 -n weather -p '{"cities":["Rome", "Tokyo","Murcia","Grasse","Heidelberg"], "rate":60}' -d "Weather ThingVisor"  
```  
  
For the ThingVisor and VirtualSilo deployments in Kubernetes it is optional to specify  
the zone where to deploy them, it can be done using the `-z` argument. If not specified,   
Kubernetes will randomly choose a node in the default zone for the deployment.  


```bash  
# Kubernetes: add the flavour yaml argument using -y and the optional zone to deploy the pod -z  
python3 f4i.py add-thingvisor -c http://[k8s_node_ip]:[NodePort] -n weather -p '{"cities":["Rome", "Tokyo","Murcia","Grasse","Heidelberg"], "rate":60}' -d "Weather ThingVisor" -y "../yaml/thingVisor-weather.yaml" -z Japan  
```  
  
Add thingVisor for oneM2M container on oneM2M of EGM in Grasse: 

```bash
# Docker
python3 f4i.py add-thingvisor -c http://[master_controller_ip]:[master_controller_port] -i fed4iot/onem2m-tv:2.2 -n EGM-Abbass -d "OneM2M data from EGM Abbass sensor" -p '{"CSEurl":"https://fed4iot.eglobalmark.com","origin":"Superman","cntArn":"Abbas123456/humidity/value","vThingName":"EGM-Abbas123456-humidity","vThingDescription":"OneM2M humidity data from EGM Abbass sensor"}'  
# Kubernetes: add the flavour yaml argument using -y and the optional zone to deploy the pod -z  
python3 f4i.py add-thingvisor -c http://[k8s_node_ip]:[NodePort] -n EGM-Abbass -d "OneM2M data from EGM Abbass sensor" -p '{"CSEurl":"https://fed4iot.eglobalmark.com","origin":"Superman","cntArn":"Abbas123456/humidity/value","vThingName":"EGM-Abbas123456-humidity","vThingDescription":"OneM2M humidity data from EGM Abbass sensor"}' -y "../yaml/thingVisor-oneM2M.yaml" -z Japan  
```  
  

Add thingVisor FIWARE Murcia, change notify_ip address with the public address of the running machine:

```bash
# Docker
python3 f4i.py add-thingvisor -c http://[master_controller_ip]:[master_controller_port] -i fed4iot/fiware-greedy-tv:2.2 -n Murcia_Sensors -p '{"ocb_service":["trafico","aparcamiento","pluviometria","tranvia","autobuses","bicis","lecturas","gps","suministro"], "ocb_ip":"fiware-dev.inf.um.es", "ocb_port":"1026"}' -d "Greedy ThingVisor for FIWARE Murcia Platform"  
# Kubernetes: add the flavour yaml argument using -y and the optional zone to deploy the pod -z  
python3 f4i.py add-thingvisor -c http://[k8s_node_ip]:[NodePort] -n Murcia_Sensors -p '{"ocb_service":["trafico","aparcamiento","pluviometria","tranvia","autobuses","bicis","lecturas","gps","suministro"], "ocb_ip":"fiware-dev.inf.um.es", "ocb_port":"1026"}' -d "Greedy ThingVisor for FIWARE Murcia Platform" -y "../yaml/thingVisor-fiWARE.yaml" -z Japan  
```  
  

Add ThingVisor Hello World:

```bash
# Docker
python3 f4i.py add-thingvisor -c http://[master_controller_ip]:[master_controller_port] -i fed4iot/helloworld-tv:2.2 -n helloWorld -d "hello thingVisor"  
# Kubernetes: add the flavour yaml argument using -y and the optional zone to deploy the pod -z  
python3 f4i.py add-thingvisor -c http://[k8s_node_ip]:[NodePort] -n helloWorld -d "hello thingVisor" -y "../yaml/thingVisor-helloWorld.yaml" -z Japan  
```  
  

HelloWorld-tv periodically produces an array of NGSI-LD entity as follows: 

```  
[{'id': 'urn:ngsi-ld:HelloSensor1', 'type': 'my-counter', 'counter': {'type': 'Property', 'value': '413'}}, {'id': 'urn:ngsi-ld:HelloSensor2', 'type': 'my-double-counter', 'double-counter': {'type': 'Property', 'value': '826'}}]  
```  
  
  
### List ThingVisor  

List ThingVisor, including info about vThingIDs of the handled virtual things:

```bash
# Docker
python3 f4i.py list-thingvisors -c http://[master_controller_ip]:[master_controller_port]  
# Kubernetes  
python3 f4i.py list-thingvisors -c http://[k8s_node_ip]:[NodePort]  
```  
  

### Logout  

Logout as admin and login as tenant1 if you prefer but some operation are forbidden as user:

```bash
# Docker
python3 f4i.py logout -c http://[master_controller_ip]:[master_controller_port]  
# Kubernetes  
python3 f4i.py logout -c http://[k8s_node_ip]:[NodePort]  
# python3 f4i.py login -u tenant1 -p password  
```  
  

### Create VirtualSilo  

Create a oneM2M based virtual Silo (this will start a flavour container for the tenant):

```bash
# Docker
python3 f4i.py create-vsilo -c http://[master_controller_ip]:[master_controller_port] -t tenant1 -f Mobius-base-f -s Silo1  
# This returns the private IP address of the vsilo broker (Mobius in this example) and the port to use for accessing, and also the port mapping by the whitch is possible to acces the broker using the  public IP address of the platform   
  
# Kubernetes, add optional zone to deploy the pod -z  
python3 f4i.py create-vsilo -c http://[k8s_node_ip]:[NodePort] -t tenant1 -f Mobius-base-f -s Silo1 -z Japan  
```  
  
  
Create FIWARE Orion based Silo2 and rawMQTT Silo3:

```bash
# create Silo2
# Docker
python3 f4i.py create-vsilo -c http://[master_controller_ip]:[master_controller_port] -t tenant1 -f orion-f -s Silo2   
# Kubernetes, add optional zone to deploy the pod -z  
python3 f4i.py create-vsilo -c http://[k8s_node_ip]:[NodePort] -t tenant1 -f orion-f -s Silo2 -z Japan  

# Now create Silo3
# Docker
python3 f4i.py create-vsilo -c http://[master_controller_ip]:[master_controller_port] -t tenant1 -f mqtt-f -s Silo3  
# Kubernetes, add optional zone to deploy the pod -z  
python3 f4i.py create-vsilo -c http://[k8s_node_ip]:[NodePort] -t tenant1 -f mqtt-f -s Silo3 -z Japan  
```  
  

### Inspect tenant   

Inspect tenant1 information:  
  
```bash
# Docker
python3 f4i.py inspect-tenant -t tenant1 -c http://[master_controller_ip]:[master_controller_port]  
# Kubernetes  
python3 f4i.py inspect-tenant -t tenant1 -c http://[k8s_node_ip]:[NodePort]  
```  
  

Browse Silo1 broker content through public IP, otherwise use docker private IP.  
Use Chrome with [ModHeader extension](https://chrome.google.com/webstore/detail/modheader/idgpnmonknjnojddfkpgkljpfnnfcklj).
Add request headers, as follows:

```  
'X-M2M-RI'   'S'  
'X-M2M-Origin'  Superman  
```  

Then access: `http://[public-ip]:[mapped_port_for_7579]/Mobius?rcn=4`.  

Browse Silo2 broker content through public IP, otherwise use docker private IP: `http://[public-ip]:[mapped port for 1026]/v2/entities`.
  

### Add VirtualThing  
  

Add some vThings to the Silo1 (oneM2M):

```bash  
python3 f4i.py add-vthing -c http://[master_controller_ip]:[master_controller_port] -t tenant1 -s Silo1 -v weather/Tokyo_temp  
python3 f4i.py add-vthing -c http://[master_controller_ip]:[master_controller_port] -t tenant1 -s Silo1 -v weather/Tokyo_pressure  
python3 f4i.py add-vthing -c http://[master_controller_ip]:[master_controller_port] -t tenant1 -s Silo1 -v EGM-Abbass/EGM-Abbas123456-humidity  
python3 f4i.py add-vthing -c http://[master_controller_ip]:[master_controller_port] -t tenant1 -s Silo1 -v Murcia_Sensors/1  
```  
  

Browse vSilo1 broker oneM2M AEs (ty=2) or containers (ty=3): `http://[public-ip]:[mapped port for 7579]/Mobius?fu=1&ty=2`.  
Get latest value of a container: `http://[public-ip]:[mapped port for 7579]/Mobius/Murcia_Sensors:1/Sensor:Aparcamiento:101/libres/la`
  
  
Add some vThings to the Silo2 (FIWARE):

```bash  
python3 f4i.py add-vthing -c http://[master_controller_ip]:[master_controller_port] -t tenant1 -s Silo2 -v weather/Tokyo_temp  
python3 f4i.py add-vthing -c http://[master_controller_ip]:[master_controller_port] -t tenant1 -s Silo2 -v weather/Tokyo_pressure  
python3 f4i.py add-vthing -c http://[master_controller_ip]:[master_controller_port] -t tenant1 -s Silo2 -v EGM-Abbass/EGM-Abbas123456-humidity  
python3 f4i.py add-vthing -c http://[master_controller_ip]:[master_controller_port] -t tenant1 -s Silo2 -v Murcia_Sensors/1  
```  
  

Browse vSilo2 Orion broker:

* `http://[public-ip]:[mapped port for 1026]/v2/entities`
* `http://[public-ip]:[mapped port for 1026]//v2/entities/urn:ngsi-ld:Sensor:Aparcamiento:101/attrs/libres`
 

Add some vThings to the Silo3 (rawMQTT):  

```bash  
python3 f4i.py add-vthing -c http://[master_controller_ip]:[master_controller_port] -t tenant1 -s Silo3 -v weather/Tokyo_temp  
python3 f4i.py add-vthing -c http://[master_controller_ip]:[master_controller_port] -t tenant1 -s Silo3 -v weather/Tokyo_pressure  
```  
  

### Add node-red for upstream demo   

From the container, enable graph plugin: `npm install node-red-contrib-graphs`. 
Connect to the public-ip and mapped docker port for `1883` to obtain publication from vSilo broker.  
One topic for vThings whose topic name is `tenant_id/vThingID`, e.g. `tenant1/weather/Tokyo_temp`.  
Example with `mosquitto_sub`:  

```bash  
mosquitto_sub -h 52.166.130.229 -p 32776 -t "#" -v  
```  

Inspect broker content using chrome to see the added oneM2M AEs as reported in deliverable D2.2.  
  

### Update ThingVisor
To send an update message to the ThingVisor. The `-u updateInfo` argument is the only not saved into the db, it is
passed to the ThingVisor and the usage depends on the ThingVisor implementation.

````bash
# to update the publication rate of the helloWorld ThingVisor and to send the updateInfo message used by the ThingVisor
python3 f4i.py update-thingvisor -c http://[master_controller_ip]:[master_controller_port] -n helloWorld -p '{"rate":1}' -d "Weather ThingVisor" -u "ephemeral information"
````

### Delete VirtualThing  

Reverse the process and clean the system.  
Delete vThings (it is possible also to directly destroy the vSilos): 

```bash  
python3 f4i.py del-vthing -c http://[master_controller_ip]:[master_controller_port] -t tenant1 -s Silo1 -v weather/Tokyo_temp  
python3 f4i.py del-vthing -c http://[master_controller_ip]:[master_controller_port] -t tenant1 -s Silo1 -v weather/Tokyo_pressure  
python3 f4i.py del-vthing -c http://[master_controller_ip]:[master_controller_port] -t tenant1 -s Silo1 -v EGM-Abbass/EGM-Abbas123456-humidity  
python3 f4i.py del-vthing -c http://[master_controller_ip]:[master_controller_port] -t tenant1 -s Silo1 -v Murcia_Sensors/1  
  
python3 f4i.py del-vthing -c http://[master_controller_ip]:[master_controller_port] -t tenant1 -s Silo2 -v weather/Tokyo_temp  
python3 f4i.py del-vthing -c http://[master_controller_ip]:[master_controller_port] -t tenant1 -s Silo2 -v weather/Tokyo_pressure  
python3 f4i.py del-vthing -c http://[master_controller_ip]:[master_controller_port] -t tenant1 -s Silo2 -v EGM-Abbass/EGM-Abbas123456-humidity  
python3 f4i.py del-vthing -c http://[master_controller_ip]:[master_controller_port] -t tenant1 -s Silo2 -v Murcia_Sensors/1  
```  
  

### Destroy VirtualSilo  

Destroy virtual Silos (this destroy the tenant container, any data is lost):

```bash  
python3 f4i.py destroy-vsilo -c http://[master_controller_ip]:[master_controller_port] -t tenant1 -s Silo1  
python3 f4i.py destroy-vsilo -c http://[master_controller_ip]:[master_controller_port] -t tenant1 -s Silo2  
python3 f4i.py destroy-vsilo -c http://[master_controller_ip]:[master_controller_port] -t tenant1 -s Silo3  
```  
  

### Delete ThingVisor  

Delete virtual ThingVisor (this will destroy the container used for the ThingVisor):

```bash  
python3 f4i.py del-thingvisor -c http://[master_controller_ip]:[master_controller_port] -n Murcia_Sensors    
python3 f4i.py del-thingvisor -c http://[master_controller_ip]:[master_controller_port] -n weather  
python3 f4i.py del-thingvisor -c http://[master_controller_ip]:[master_controller_port] -n EGM-Abbass  
```  


### Delete Flavour  

Delete flavour: 

```bash  
python3 f4i.py del-flavour -c http://[master_controller_ip]:[master_controller_port] -n Mobius-base-f  
python3 f4i.py del-flavour -c http://[master_controller_ip]:[master_controller_port] -n orion-f  
python3 f4i.py del-flavour -c http://[master_controller_ip]:[master_controller_port] -n mqtt-f  
```  
  

### Check if system empty   

Now system should be empty: 

```bash  
python3 f4i.py list-flavours -c http://[master_controller_ip]:[master_controller_port]  
python3 f4i.py list-thingvisors -c http://[master_controller_ip]:[master_controller_port]  
python3 f4i.py list-vsilos -c http://[master_controller_ip]:[master_controller_port]  
python3 f4i.py inspect-tenant -c http://[master_controller_ip]:[master_controller_port] -t tenant1  
``` 
