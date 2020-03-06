  
# README  
This is the instructions to quickly setup an instance of the VirIoT platform being developed
by the [Fed4IoT](https://fed4iot.org) EU-Japan project.
Setup of this demo configuration was tested on Ubuntu 18.04.  
  

Activate python3 and bash autocomplete:  

```bash  
sudo apt-get install python3-argcomplete   
sudo activate-global-python-argcomplete3  
```  
  

### Optional building of docker images:  

Images of VirIoT components are available in [DockerHub](https://hub.docker.com/u/fed4iot). Optionally they can be built locally as follows.  

#### ThingVisors  

Build the necessary ThingVisor images by using "fed4iot" as prefix and "-tv" as suffix for indicating that it is a ThingVisor. For instance:  

```bash  
cd Thingvisors/DockerThingVisor/ThingVisor_HelloWorld  
docker build -t fed4iot/helloworld-tv .  
```  

#### Flavours  

Build the necessary flavour images by using "fed4iot" as prefix and "-f" as suffix for indicating that it is a flavour. For instance:  

```bash  
cd Flavours/mobius-base-flavour/  
docker build -t fed4iot/mobius-base-f .  
```  
  

#### Master-Controller  

Build the master-controller image. Right now it is working only for Kubernetes configuration.  

```bash  
cd Master-Controller/  
docker build -t fed4iot/master-controller .  
```  
  

## Initial configurations for Docker-based deployment on a single machine:  
  

* open ports from `32768` to `61000`  
* python3 with `flask flask_cors pymongo paho-mqtt docker`, if not present use `pip3 install`  
* `mosquitto` running  
* `docker` running with docker0 bridge address space `172.17.0.1/16`  
  

Run a Mongo container for storing system state. Mongo is reachable through `32768` on public IP.  
  

```bash  
docker run -d --name mongo-container -p 32768:27017 mongo:3.4.18  
```  
  

If already run but stopped, use `docker start mongo-container`.  
To reset the DB delete the container and run it again.  
To explore DB use `mongo-compass` and connect to the ip address of the container.  
  

Configure the right IP addresses and ports editing the settings template file `settings-docker-template.py` with your correct configurations and copy it to the `Master-Controller/data` folder.  
  

```bash  
cd Master-Controller  
# edit settings-docker-template.py  
vim settings-docker-template.py  
# after the edits copy and rename it to data/settings.py  
cp settings-docker-template.py data/settings.py  
```  
  

Install all the dependencies required using `pip3`:  
  

```bash  
# for install all dependencies use the file requirements.txt in the folder Master-Controller  
pip3 install -r requirements.txt  
```  
  

The file `db_setup.py` is used by `master-controller.py` for setting parameters for the 'admin' user with password 'passw0rd'  
  

Run the master controller:  

```bash  
python3 master-controller.py  
```  
  

## Initial configurations for Kubernetes-based deployment:  
  

### Kubernetes cluster setup  

Kubernetes documentation: <https://kubernetes.io/docs/setup/production-environment/tools/kubeadm/create-cluster-kubeadm/>.  
  

### VirIoT Files on k8s master node  

The Master-Controller and YAML folders of the repository must be available on the k8s master node `$HOME/VirIoT` directory.  
Unless differently specified, next commands are run from the k8s master node.  
  

### Node labelling from k8s master node  

We consider a kubernetes distributed cluster formed by a default zone and (optional) edge zones. Default zone has no "zone" label.  Nodes of an edge zone must be labelled with "zone" and "gw" labels, as follows. The value of the "gw" key must contain a public IP address through which it is possible to access the edge cluster.   
  

```bash  
kubectl label nodes <NodeName> zone=<ZoneName>  
kubectl label nodes <NodeName> gw=<gatewayIP>  
  
#e.g.: kubectl label nodes node2 zone=Japan  
#e.g.: kubectl label nodes node2 gw=162.80.82.44  
  
# to see labelling results....  
kubectl get nodes -L gw -L zone  
```   

### Setup MQTT cluster from k8s master node (one VerneMQ broker per node)   

VerneMQ deployed as a StatefulSet to each node.  
  
Edit the `spec.replicas` with the correct number of nodes in the cluster.  
  

```bash  
# Edit number of available nodes in yaml/vernemq-affinity.yaml  
vim $HOME/VirIoT/yaml/vernemq-affinity.yaml  
# edit spec.replicas: <NumberOfReplicas>  
#e.g. if you have a cluster composed of two nodes: spec.replicas:2  
kubectl apply -f $HOME/VirIoT/yaml/vernemq-affinity.yaml  
# to get the currently deployed pods  
kubectl get pods -o wide  
```  
  

### Setup MongoDB system database from k8s master node  

Create the MongoDB statefulset and service resources applying the yaml:  

```bash  
kubectl apply -f $HOME/VirIoT/yaml/mongo-statefulset-noauth.yaml  
# to get the currently deployed pods  
kubectl get pods -o wide  
```  
  
  

### VirIoT Master-Controller execution as Pod from k8s master node:  

The Master-Controller is deployed as a StatefulSet inside the cluster default zone. Edit the Master-Controller configuration in `$HOME/VirIoT/Master-Controller/yaml/viriot-configmap-setup.yaml` and create the ConfigMap resource, as well as the Master-Controller.

```bash    
# edit Master-Controller configuration
vim $HOME/VirIoT/Master-Controller/yaml/viriot-configmap-setup.yaml
# apply ConfigMap resource
kubectl apply -f $HOME/VirIoT/Master-Controller/yaml/viriot-configmap-setup.yaml 
# deploy the Master-Controller applying the yaml
kubectl apply -f $HOME/VirIoT/yaml/master-controller.yaml  
# to get the currently deployed pods  
kubectl get pods -o wide  
kubectl get service f4i-master-controller-svc  
```  
  

### VirIoT Master-Controller execution locally on kubernetes master node:  
Copy and rename the settings template file `$HOME/VirIoT/Master-Controller/settings-kubernetes-template.py` in  `$HOME/VirIoT/Master-Controller/data/settings.py`.
Then edit the new `settings.py` file modifying the IP addresses and ports according with your configurations.  
  
```bash    
cp $HOME/VirIoT/Master-Controller/settings-kubernetes-template.py $HOME/VirIoT/Master-Controller/data/settings.py  
# edit the "data/settings.py" as preferred, and be sure to edit the variable master_controller_in_container=False  
vim $HOME/VirIoT/Master-Controller/data/settings.py
```  
  

## Command Line Interface  
  

Now use the CLI (or POSTMAN).  Install `PyYAML`:
```bash
pip3 install PyYAML
```
Now you can use `python3 f4i.py` and press tab for autocomplete, for help you can use `python3 f4i.py -h`.  Furthermore, you can use for example  `python3 f4i.py create-vsilo -h` for sub-help.  
  
When using **Kubernetes** the commands are the same as the ones used with Docker except  the ip address.  
```bash  
# to know the ClusterIP related to the Master-Controller service:  
kubectl get svc f4i-master-controller-svc 
```  
You can use different options:  
 
1. The ip address of the ClusterIP of the Master-Controller service along with the 8090 port.
2. The ip address of any node of the cluster, along with the NodePort of the Master-Controller service.
3. If set, the external ip address of any node of the cluster, followed by the NodePort of the Master-Controller service.
  

Move to CLI directory to use the Command Line Interface.   
  

```bash  
cd $HOME/VirIoT/CLI  
```  

### Login  
Login as `admin`. Access control uses JWT (JSON Web Token).  
Latest access token stored in $HOME/.viriot/token and used for every inteaction with the master controller.  

```bash  
python3 f4i.py login -c http://[master_controller_ip]:[master_controller_port] -u admin -p passw0rd  
```  
  

### Register  

As 'admin' register user 'tenant1' with password 'password' and role 'user'  

```bash  
python3 f4i.py register -c http://[master_controller_ip]:[master_controller_port] -u tenant1 -p password -r user  
```  
  

### Add Flavour  
There are already several vSilo Flavours available.

#### MOBIUS (for developers that want to use the oneM2M IoT standard)
Add a vSilo flavour for [Mobius](https://github.com/IoTKETI/Mobius).
Mobius is a [oneM2M](http://www.onem2m.org) server implementation.
It got the oneM2M certification and it is designated as one of the golden samples.

```bash  
python3 f4i.py add-flavour -c http://[master_controller_ip]:[master_controller_port] -f Mobius-base-f -s Mobius -i fed4iot/mobius-base-f:2.2 -d "silo with a oneM2M Mobius broker"  
# Kubernetes: add the flavour yaml argument using -y   
python3 f4i.py add-flavour -c http://[k8s_node_ip]:[NodePort] -f Mobius-base-f -s Mobius -d "silo with a oneM2M Mobius broker" -y "yaml/flavours-mobius-base.yaml"   
```  


#### ORION (for developers that want to use the FIWARE NGSIv2 IoT standard)
Add a vSilo flavour for [Orion](https://fiware-orion.readthedocs.io/en/master/).
Orion is a C++ implementation of the [NGSIv2](https://fiware.github.io/specifications/ngsiv2/stable/) REST API
binding developed as a part of the FIWARE platform.

```bash  
python3 f4i.py add-flavour -c http://[master_controller_ip]:[master_controller_port] -f orion-f -i fed4iot/orion-f:2.2 -d "silo with a FIWARE Orion broker" -s ""  
# Kubernetes: add the flavour yaml argument using -y   
python3 f4i.py add-flavour -c http://[k8s_node_ip]:[NodePort] -f orion-f -d "silo with a FIWARE Orion broker" -s "" -y "yaml/flavours-orion.yaml"  
```  

#### SCORPIO (for developers that want to use the ETSI NGSI-LD standard for IoT and context data)
Add a vSilo flavour for [Scorpio](https://github.com/ScorpioBroker/ScorpioBroker).
Scorpio is an [NGSI-LD](https://www.etsi.org/deliver/etsi_gs/CIM/001_099/009/01.02.02_60/gs_CIM009v010202p.pdf)
compliant context broker developed by NEC Laboratories Europe and NEC Technologies India.
NGSI-LD is an open API and Datamodel specification for context management published by ETSI.
Scorpio is developed in Java using the SpringCloud microservices framework.

```bash  
python3 f4i.py add-flavour -c http://[master_controller_ip]:[master_controller_port] -f ngsild-scorpio-f -i fed4iot/ngsild-scorpio-f:2.2 -d "silo with a Scorpio NGSI-LD broker" -s ""  
# Kubernetes: add the flavour yaml argument using -y   
python3 f4i.py add-flavour -c http://[k8s_node_ip]:[NodePort] -f ngsild-scorpio-f -d "silo with a Scorpio NGSI-LD broker" -s "" -y "yaml/flavours-ngsild-scorpio.yaml"  
```  


#### RAW MQTT
Add a vSilo flavour for exporting your raw IoT data to MQTT topics.

```bash  
python3 f4i.py add-flavour -c http://[master_controller_ip]:[master_controller_port] -f mqtt-f -i fed4iot/raw-mqtt-f:2.2 -d "silo with a Mosquitto broker" -s ""  
# Kubernetes: add the flavour yaml argument using -y   
python3 f4i.py add-flavour -c http://[k8s_node_ip]:[NodePort] -f mqtt-f -d "silo with a Mosquitto broker" -s "" -y "yaml/flavours-raw-mqtt.yaml"  
```  
  

### List flavours  

```bash  
python3 f4i.py list-flavours -c http://[master_controller_ip]:[master_controller_port]  
# Kubernetes  
python3 f4i.py list-flavours -c http://[k8s_node_ip]:[NodePort]  
```  
  

### Add ThingVisor  

Add ThingVisor v-weather with some cities.  
  

```bash  
python3 f4i.py add-thingvisor -c http://[master_controller_ip]:[master_controller_port] -i fed4iot/v-weather-tv:2.2 -n weather -p "{'cities':['Rome', 'Tokyo','Murcia','Grasse','Heidelberg'], 'rate':60}" -d "Weather ThingVisor"  
```  
  

For the ThingVisor and VirtualSilo deployments in Kubernetes it is optional to specify  
the zone where to deploy them with the '-z' argument. If not specified,   
Kubernetes will randomly choose a zone for the deployment in the available   
fed4iot node pool.  
  

```bash  
# Kubernetes: add the flavour yaml argument using -y and the optional zone to deploy the pod -z  
python3 f4i.py add-thingvisor -c http://[k8s_node_ip]:[NodePort] -n weather -p "{'cities':['Rome', 'Tokyo','Murcia','Grasse','Heidelberg'], 'rate':60}" -d "Weather ThingVisor" -y "yaml/thingVisor-weather.yaml" -z Honolulu  
```  
  

Add thingVisor for oneM2M container on oneM2M of EGM in Grasse. Change poaIP with public IP address of running machines   

```bash  
python3 f4i.py add-thingvisor -c http://[master_controller_ip]:[master_controller_port] -i fed4iot/onem2m-tv:2.2 -n EGM-Abbass -d "OneM2M data from EGM Abbass sensor" -p "{'CSEurl':'https://fed4iot.eglobalmark.com','origin':'Superman', 'poaPort':'8089','cntArn':'Abbas123456/humidity/value','poaIP':'127.0.0.1','vThingName':'EGM-Abbas123456-humidity','vThingDescription':'OneM2M humidity data from EGM Abbass sensor'}"  
# Kubernetes: add the flavour yaml argument using -y and the optional zone to deploy the pod -z  
python3 f4i.py add-thingvisor -c http://[k8s_node_ip]:[NodePort] -n EGM-Abbass -d "OneM2M data from EGM Abbass sensor" -p "{'CSEurl':'https://fed4iot.eglobalmark.com','origin':'Superman', 'poaPort':'8089','cntArn':'Abbas123456/humidity/value','poaIP':'127.0.0.1','vThingName':'EGM-Abbas123456-humidity','vThingDescription':'OneM2M humidity data from EGM Abbass sensor'}" -y "yaml/thingVisor-oneM2M.yaml" -z Honolulu  
```  
  

Add thingVisor FIWARE Murcia, change notify_ip address with the public address of the running machine  

```bash  
python3 f4i.py add-thingvisor -c http://[master_controller_ip]:[master_controller_port]  -i fed4iot/fiware-greedy-tv:2.2 -n Murcia_Sensors -p '{"ocb_service":["trafico","aparcamiento","pluviometria","tranvia","autobuses","bicis","lecturas","gps","suministro"], "ocb_ip":"fiware-dev.inf.um.es", "ocb_port":"1026", "notificacion_protocol":"http", "notify_ip":"52.166.130.229"}' -d "Greedy ThingVisor for FIWARE Murcia Platform"  
# Kubernetes: add the flavour yaml argument using -y and the optional zone to deploy the pod -z  
python3 f4i.py add-thingvisor -c http://[k8s_node_ip]:[NodePort] -n Murcia_Sensors -p '{"ocb_service":["trafico","aparcamiento","pluviometria","tranvia","autobuses","bicis","lecturas","gps","suministro"], "ocb_ip":"fiware-dev.inf.um.es", "ocb_port":"1026", "notificacion_protocol":"http", "notify_ip":"52.166.130.229"}' -d "Greedy ThingVisor for FIWARE Murcia Platform" -y "yaml/thingVisor-fiWARE.yaml" -z Honolulu  
```  
  

Add ThingVisor Hello World  

```bash  
python3 f4i.py add-thingvisor -c http://[master_controller_ip]:[master_controller_port] -i fed4iot/helloworld-tv:2.2 -n helloWorld -d "hello thingVisor"  
# Kubernetes: add the flavour yaml argument using -y and the optional zone to deploy the pod -z  
python3 f4i.py add-thingvisor -c http://[k8s_node_ip]:[NodePort] -n helloWorld -d "hello thingVisor" -y "yaml/thingVisor-helloWorld.yaml" -z Honolulu  
```  
  

Helloworld-tv periodically produces an array of NGSI-LD entity as follows  

```  
[{'id': 'urn:ngsi-ld:HelloSensor1', 'type': 'my-counter', 'counter': {'type': 'Property', 'value': '413'}}, {'id': 'urn:ngsi-ld:HelloSensor2', 'type': 'my-double-counter', 'double-counter': {'type': 'Property', 'value': '826'}}]  
```  
  
  

### List ThingVisor  

List ThingVisor, including info about vThingIDs of the handled virtual things   

```bash  
python3 f4i.py list-thingvisors -c http://[master_controller_ip]:[master_controller_port]  
# Kubernetes  
python3 f4i.py list-thingvisors -c http://[k8s_node_ip]:[NodePort]  
```  
  

### Logout  

Logout as admin and login as tenant1 if you prefer but some operation are forbidden as user  

```bash  
python3 f4i.py logout -c http://[master_controller_ip]:[master_controller_port]  
# Kubernetes  
python3 f4i.py logout -c http://[k8s_node_ip]:[NodePort]  
# python3 f4i.py login -u tenant1 -p password  
```  
  

### Create VirtualSilo  

Create a oneM2M based virtual Silo (this will start a flavour container for the tenant)  

```bash  
python3 f4i.py create-vsilo -c http://[master_controller_ip]:[master_controller_port] -t tenant1 -f Mobius-base-f -s Silo1  
# This returns the private IP address of the vsilo broker (Mobius in this demo) and the port to use for accessing, and also the port mapping by the whitch is possible to acces the broker using the  public IP address of the platform   
  
# Kubernetes, add optional zone to deploy the pod -z  
python3 f4i.py create-vsilo -c http://[k8s_node_ip]:[NodePort] -t tenant1 -f Mobius-base-f -s Silo1 -z Honolulu  
```  
  
  

Create FIWARE Orion based Silo2 and rawMQTT Silo3  

```bash  
python3 f4i.py create-vsilo -c http://[master_controller_ip]:[master_controller_port] -t tenant1 -f orion-f -s Silo2   
# Kubernetes, add optional zone to deploy the pod -z  
python3 f4i.py create-vsilo -c http://[k8s_node_ip]:[NodePort] -t tenant1 -f orion-f -s Silo2 -z Honolulu  
  
python3 f4i.py create-vsilo -c http://[master_controller_ip]:[master_controller_port] -t tenant1 -f mqtt-f -s Silo3  
# Kubernetes, add optional zone to deploy the pod -z  
python3 f4i.py create-vsilo -c http://[k8s_node_ip]:[NodePort] -t tenant1 -f mqtt-f -s Silo3 -z Honolulu  
```  
  

### Inspect tenant   

Inspect tenant1 information:  
  

```bash  
python3 f4i.py inspect-tenant -t tenant1 -c http://[master_controller_ip]:[master_controller_port]  
# Kubernetes  
python3 f4i.py inspect-tenant -t tenant1 -c http://[k8s_node_ip]:[NodePort]  
```  
  

Browse Silo1 broker content through public IP, otherwise use docker private IP.  
Use Chrome with ModHeader extension. Add request headers   

```  
'X-M2M-RI'   'S'  
'X-M2M-Origin'  Superman  
```  

Then access: http://[public-ip]:[mapped port for 7579]/Mobius?rcn=4  
  
  

Browse Silo2 broker content through public IP, otherwise use docker private IP: http://[public-ip]:[mapped port for 1026]/v2/entities  
  

### Add VirtualThing  
  

Add some vThings to the Silo1 (oneM2M)  

```bash  
python3 f4i.py add-vthing -c http://[master_controller_ip]:[master_controller_port] -t tenant1 -s Silo1 -v weather/Tokyo_temp  
python3 f4i.py add-vthing -c http://[master_controller_ip]:[master_controller_port] -t tenant1 -s Silo1 -v weather/Tokyo_pressure  
python3 f4i.py add-vthing -c http://[master_controller_ip]:[master_controller_port] -t tenant1 -s Silo1 -v EGM-Abbass/EGM-Abbas123456-humidity  
python3 f4i.py add-vthing -c http://[master_controller_ip]:[master_controller_port] -t tenant1 -s Silo1 -v Murcia_Sensors/1  
```  
  

Browse vSilo1 broker oneM2M AEs (ty=2) or containers (ty=3): http://[public-ip]:[mapped port for 7579]/Mobius?fu=1&ty=2.  
Get latest value of a container: http://[public-ip]:[mapped port for 7579]/Mobius/Murcia_Sensors:1/Sensor:Aparcamiento:101/libres/la  
  
  

Add some vThings to the Silo2 (FIWARE)  

```bash  
python3 f4i.py add-vthing -c http://[master_controller_ip]:[master_controller_port] -t tenant1 -s Silo2 -v weather/Tokyo_temp  
python3 f4i.py add-vthing -c http://[master_controller_ip]:[master_controller_port] -t tenant1 -s Silo2 -v weather/Tokyo_pressure  
python3 f4i.py add-vthing -c http://[master_controller_ip]:[master_controller_port] -t tenant1 -s Silo2 -v EGM-Abbass/EGM-Abbas123456-humidity  
python3 f4i.py add-vthing -c http://[master_controller_ip]:[master_controller_port] -t tenant1 -s Silo2 -v Murcia_Sensors/1  
```  
  

Browse vSilo2 Orion broker   

* http://[public-ip]:[mapped port for 1026]/v2/entities  
* http://[public-ip]:[mapped port for 1026]//v2/entities/urn:ngsi-ld:Sensor:Aparcamiento:101/attrs/libres  
  
  

Add some vThings to the Silo3 (rawMQTT):  

```bash  
python3 f4i.py add-vthing -c http://[master_controller_ip]:[master_controller_port] -t tenant1 -s Silo3 -v weather/Tokyo_temp  
python3 f4i.py add-vthing -c http://[master_controller_ip]:[master_controller_port] -t tenant1 -s Silo3 -v weather/Tokyo_pressure  
```  
  

### Add node-red for upstream demo   

npm install node-red-contrib-graphs from the container to enable graph plugin.  
Connect to the public-ip and mapped docker port for 1883 to obtain pubblicatin from vSilo broker.  
One topic for vThings whose topicname is tenant_id/vThingID, e.g. tenant1/weather/Tokyo_temp.  
Example with `mosquitto_sub`:  

```bash  
mosquitto_sub -h 52.166.130.229 -p 32776 -t "#" -v  
```  

Inspect broker content using chrome to see the added oneM2M AEs as reported in deliverable D2.2.  
  
  

### Delete VirtualThing  

Reverse the process and clean the system.  
Delete vThings (it is possible also to directly destroy the vSilos)  

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

Destroy virtual Silos (this destroy the tenant container, any data is lost)  

```bash  
python3 f4i.py destroy-vsilo -c http://[master_controller_ip]:[master_controller_port] -t tenant1 -s Silo1  
python3 f4i.py destroy-vsilo -c http://[master_controller_ip]:[master_controller_port] -t tenant1 -s Silo2  
python3 f4i.py destroy-vsilo -c http://[master_controller_ip]:[master_controller_port] -t tenant1 -s Silo3  
```  
  

### Delete ThingVisor  

Delete virtual ThingVisor (this will destroy the contaier used for the ThingVisor)  

```bash  
python3 f4i.py del-thingvisor -c http://[master_controller_ip]:[master_controller_port] -n Murcia_Sensors    
python3 f4i.py del-thingvisor -c http://[master_controller_ip]:[master_controller_port] -n weather  
python3 f4i.py del-thingvisor -c http://[master_controller_ip]:[master_controller_port] -n EGM-Abbass  
```  
  

### Delete Flavour  

Delete flavour  

```bash  
python3 f4i.py del-flavour -c http://[master_controller_ip]:[master_controller_port] -n Mobius-base-f  
python3 f4i.py del-flavour -c http://[master_controller_ip]:[master_controller_port] -n orion-f  
python3 f4i.py del-flavour -c http://[master_controller_ip]:[master_controller_port] -n mqtt-f  
```  
  

### Check if system empty   

Now system should be empty  

```bash  
python3 f4i.py list-flavours -c http://[master_controller_ip]:[master_controller_port]  
python3 f4i.py list-thingvisors -c http://[master_controller_ip]:[master_controller_port]  
python3 f4i.py list-vsilos -c http://[master_controller_ip]:[master_controller_port]  
python3 f4i.py inspect-tenant -c http://[master_controller_ip]:[master_controller_port] -t tenant1  
``` 
