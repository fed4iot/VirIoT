# Kubernetes Deployment  

(Please notice that images of VirIoT components are available in the [project's DockerHub](https://hub.docker.com/u/fed4iot). 
Optionally, they can be built locally. See [here](Optional%20docker%20build.md) for instructions).


### Kubernetes (v1.18) cluster setup  

To properly setup a multi-node Kubernetes cluster, see the Kubernetes documentation: <https://kubernetes.io/docs/setup/production-environment/tools/kubeadm/create-cluster-kubeadm/>.  

Kubernetes cluster should support [service topology](https://kubernetes.io/docs/concepts/services-networking/service-topology/) feature of Kubernetes for performance (traffic, delay) optimization. To this end, kubeadm needs an additional config file [k8s_config.yaml](../yaml/k8s_config.yaml). We assumed to use [Flannel](https://github.com/coreos/flannel#flannel) network plug-in (podSubnet: "10.244.0.0/16").

```bash  
kubeadm init --config k8s_config.yaml 
```  

Alternatively, you can [install Kubernetes with Minikube](https://kubernetes.io/docs/setup/learning-environment/minikube/). Minikube is a tool that makes it easy to run Kubernetes locally. Minikube runs a single-node Kubernetes cluster inside a Virtual Machine (VM) on your laptop for users looking to try out Kubernetes. In this case, having just one node, support for service topology (see above) is not needed.


## Initial configurations
### Clone Git Repository

```bash  
git clone https://github.com/fed4iot/VirIoT.git
cd VirIoT  
```

### VirIoT Files on k8s master node  

The Master-Controller and YAML folders of the repository must be available on the k8s master node `VirIoT` directory.  
Unless differently specified, the following commands are run from the k8s master node.  

### Node labelling from k8s master node  

**VirIoT labels**

We consider a Kubernetes distributed cluster formed by a default zone and (optionally) multiple "edge" zones. 
Each zone has a gateway node with a public IP address through which it is possible to access the k8s nodes of the zone. The gateway node is any k8s node of the zone with a public IP address, and it hosts the MQTT broker and the HTTP proxy that are used by all VirIoT vSilos and ThingVisor of the zone.

The involved labels are: `viriot-zone`, `viriot-gw`, and `viriot-zone-gw`.

The default zone has `viriot-zone` label (`default`). Nodes of an edge zone must be labelled with `viriot-zone` and `viriot-gw` labels. The value of the `viriot-gw` key must contain a public IP address through which it is possible to access the edge cluster.

A single node per viriot-zone **must** have the label `viriot-zone-gw=true`.


```bash  
kubectl label nodes <NodeName> viriot-zone=<ZoneName>
kubectl label nodes <NodeName> viriot-zone-gw=true   
kubectl label nodes <NodeName> viriot-gw=<gatewayIP>  
 
# e.g.: kubectl label nodes node2 viriot-zone=Japan  
# e.g.: kubectl label nodes node2 viriot-zone-gw=true  
# e.g.: kubectl label nodes node2 viriot-zone=Japan 
# to see labelling results....  
kubectl get nodes -L viriot-gw -L viriot-zone  
```
 
Thus if you are running on Minikube for test purposes, you have to issue at least the following command to get your single-node cluster up and running (since the node's name usually is *minikube*):
```bash  
kubectl label nodes minikube viriot-zone-gw=true 
```
 

**Kubernetes labels for service topology feature**

Every kubernetes node must have the label `topology.kubernetes.io/zone` equal to the `viriot-zone` label (this is default behaviour in the 'default' zone). 

```bash 
kubectl label nodes <NodeName> topology.kubernetes.io/zone=<ZoneName>
# e.g.: kubectl label nodes node2 topology.kubernetes.io/zone=Japan
# to see labelling results....  
kubectl get nodes -L viriot-gw -L topology.kubernetes.io/zone  
```   

A possible output for a configuratin made of a default (vm2,vm3,vm4) an a japan (vmjp1,vmjp2) zones is the following:


```bash
kubectl get nodes -L viriot-zone,viriot-gw,viriot-zone-gw,topology.kubernetes.io/zone

NAME                  STATUS   ROLES    AGE   VERSION   VIRIOT-ZONE   VIRIOT-GW       VIRIOT-ZONE-GW   ZONE

vm1                   Ready    master   61d   v1.18.5                                                  

vm2                   Ready    <none>   61d   v1.18.5   default       13.80.153.4     true             default

vm3                   Ready    <none>   61d   v1.18.5   default       13.80.153.4                      default

vm4                   Ready    <none>   61d   v1.18.5   default       13.80.153.4                      default

vmjp1                 Ready    <none>   61d   v1.17.0   japan         13.78.102.196   true             japan

vmjp2                 Ready    <none>   61d   v1.17.4   japan         13.78.102.196                    japan

``` 

### Setup MQTT services for control/telemetry data from k8s master node (one VerneMQ broker per viriot-zone)

Deploy VerneMQ as a StatefulSet to nodes that have `viriot-zone-gw=true`.  
 
Edit the `spec.replicas` with the correct number of used cluster nodes.  


```bash  
# Edit number of available nodes in yaml/vernemq-affinity.yaml  
vim yaml/vernemq-affinity.yaml  
# edit spec.replicas: <NumberOfReplicas>  
#e.g. if you have a cluster composed of two nodes: spec.replicas:2  
kubectl apply -f yaml/vernemq-affinity.yaml  
# to get the currently deployed pods  
kubectl get pods -o wide  
```  

### Setup HTTP services for large contents (images, streams, etc.) from k8s master node (one nginx server per viriot-zone)

Deploy nginx as a deployment to nodes that have `viriot-zone-gw=true`.  
 
Edit the `spec.replicas` with the correct number of used cluster nodes.  


```bash  
# Edit number of available nodes in yaml/vernemq-affinity.yaml  
vim yaml/viriot-http-proxy.yaml  
# edit spec.replicas: <NumberOfReplicas>  
#e.g. if you have a cluster composed of two nodes: spec.replicas:2  
kubectl apply -f yaml/viriot-http-proxy.yaml  
# to get the currently deployed pods  
kubectl get pods -o wide  
```    


### Setup MongoDB system database from k8s master node  

Create the MongoDB statefulset and service resources applying the yaml:  

```bash  
kubectl apply -f yaml/mongo-statefulset-noauth.yaml  
# to get the currently deployed pods  
kubectl get pods -o wide  
```  
  

### VirIoT Master-Controller execution
The Master-Controller can be executed using two approaches:
1. [VirIoT Master-Controller execution as Pod from k8s master node](#option-1-viriot-master-controller-execution-as-pod-from-k8s-master-node)
2. [VirIoT Master-Controller execution locally on kubernetes master node](#option-2-viriot-master-controller-execution-locally-on-kubernetes-master-node)

#### [Option 1] VirIoT Master-Controller execution as Pod from k8s master node

The Master-Controller is deployed as a StatefulSet inside the cluster's default zone. 
Edit the Master-Controller configuration in `yaml/viriot-configmap-setup.yaml` modifying the IP addresses 
and ports according to your infrastructure (usually you would only need to change the 
default_gateway_IP = "" variable to the public IP of the node hosting the Master-Controller). 
Then create the ConfigMap resource, as well as the Master-Controller.

```bash    
# edit Master-Controller configuration
vim yaml/viriot-configmap-setup.yaml
# apply ConfigMap resource
kubectl apply -f yaml/viriot-configmap-setup.yaml 
# deploy the Master-Controller applying the yaml
kubectl apply -f yaml/master-controller.yaml  
# to get the currently deployed pods  
kubectl get pods -o wide  
kubectl get service f4i-master-controller-svc  
```  

The master controller is now running as a Pod.
  

#### [Option 2] VirIoT Master-Controller execution locally on kubernetes master node  
Copy and rename the settings template file `Master-Controller/settings-kubernetes-template.py` in `Master-Controller/data/settings.py`.
Then edit the new `settings.py` file modifying the IP addresses and ports according with your configurations.  
  
```bash    
cp Master-Controller/settings-kubernetes-template.py Master-Controller/data/settings.py  
# edit the "data/settings.py" as preferred, and be sure to edit the variable master_controller_in_container=False  
vim Master-Controller/data/settings.py
```  

Run the master controller:  

```bash  
python3 master-controller.py  
```  
    
