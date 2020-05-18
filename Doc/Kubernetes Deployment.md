# Kubernetes Deployment  

Images of VirIoT components are available in [DockerHub](https://hub.docker.com/u/fed4iot). 
Optionally, they can be built locally as [follows](Optional%20docker%20build.md). 

### Optional building of docker images:  

Images of VirIoT components are available in [DockerHub](https://hub.docker.com/u/fed4iot). Optionally they can be built locally as follows.  

### Kubernetes cluster setup  

To properly setup a Kubernetes cluster, see the Kubernetes documentation: <https://kubernetes.io/docs/setup/production-environment/tools/kubeadm/create-cluster-kubeadm/>.  
  
 
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

We consider a Kubernetes distributed cluster formed by a default zone and (optionally) multiple edge zones. 
The default zone has no "viriot-zone" label. Nodes of an edge zone must be labelled with "viriot-zone" and "viriot-gw" labels, as follows: 
the value of the "viriot-gw" key must contain a public IP address through which it is possible to access the edge cluster.   


```bash  
kubectl label nodes <NodeName> viriot-zone=<ZoneName>  
kubectl label nodes <NodeName> viriot-gw=<gatewayIP>  
  
#e.g.: kubectl label nodes node2 viriot-zone=Japan  
#e.g.: kubectl label nodes node2 viriot-gw=162.80.82.44  
  
# to see labelling results....  
kubectl get nodes -L viriot-gw -L viriot-zone  
```   

### Setup MQTT cluster from k8s master node (one VerneMQ broker per node)

VerneMQ deployed as a StatefulSet to each node.  
 
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

The Master-Controller is deployed as a StatefulSet inside the cluster default zone. 
Edit the Master-Controller configuration in `yaml/viriot-configmap-setup.yaml` modifying the IP addresses 
and ports according to your infrastructure (usually you would only need to change the 
default_gateway_IP = "" variable to the public IP of the node hosting the Master-Controller. 
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
    
