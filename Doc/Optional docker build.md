# Optional: building of docker images  

### ThingVisors  

Build the necessary ThingVisor images by using "fed4iot" as prefix and "-tv" as suffix for indicating that it is a ThingVisor. For instance:  

```bash  
cd Thingvisors/DockerThingVisor/ThingVisor_HelloWorld  
docker build -t fed4iot/helloworld-tv .  
```  

### Flavours  

Build the necessary flavour images by using "fed4iot" as prefix and "-f" as suffix for indicating that it is a flavour. For instance:  

```bash  
cd Flavours/mobius-base-flavour/  
docker build -t fed4iot/mobius-base-f .  
```  
  

### Master-Controller  

Build the master-controller image. Right now it is working only for Kubernetes configuration.  

```bash  
cd Master-Controller/  
docker build -t fed4iot/master-controller .  
```  
  