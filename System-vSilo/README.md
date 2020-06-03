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


## How To Browse Data in System vSilo
The System vSilo implements the standard NGSI-LD API, as specified in the NGSI-LD API HTTP binding.
The main entry-point for querying data is the /entities REST resource.
For instance, if you add a Weather ThingVisor to the system, with a command similar to:

```bash
f4i.py add-thingvisor -n weather -p "{'cities':['Rome', 'Tokyo','Grasse','Heidelberg'], 'rate':60}" -d "Weather ThingVisor"
```

The Sytem vSilo will immediately start incorporating data from all virtual things managed by the Weather ThingVisor, making them available as NGSI-LD Entities under the /entities endpoint.

Let's assume we want to know where there is a high level of humidity, then we can issue a query, as follows:

```bash
GET /ngsi-ld/v1/entities/?q=hygrometer.value>=60
```

Getting back results as follows:

```bash
[
{
  "id": "urn:ngsi-ld:Tokyo:humidity",
  "type": "humidity",
  "hygrometer": {
    "type": "Property",
    "value": 94
  }
}
,
{
  "id": "urn:ngsi-ld:Grasse:humidity",
  "type": "humidity",
  "hygrometer": {
    "type": "Property",
    "value": 64
  }
}
]
```

The query language also supports geospatial queries, as follows:

```bash
GET /ngsi-ld/v1/entities/?q={"location.value":{"$near":{"$geometry":{"type":"Point","coordinates": [ -1.1294058,37.9942698 ] },"$maxDistance":400}}}
```

The above query will return all entities that are in a range of 400 meters far away from the point located at [ -1.1294058,37.9942698 ].


## How To Discover Data in System vSilo
The System vSilo has several features to allow users query for available Entity Types and Attributes.
Discovery means the ability to find out what kind of information is available in an NGSI-LD system. These features are additional to what is part of the current NGSI-LD specification.

Version 1.2.2 of the currently NGSI-LD API only supports the request for entities based on specific entities identifiers, entity types and attributes. This implies that the user has to have a detsailed prior knowledge of the data structures.
When this is not the case, requests for available entity types are to be ssupported.
The System vSilo's Discovery capabilities aims precisely at this.
Since attributes are on the same indexing level as entity types, requests for available attributes are also supported by the System vSilo Discovery feature.

```bash
GET /ngsi-ld/v1/types
```

Will return an array of Entity Type Information comprising
* id: URI/name of entity type being described
* type: "EntityType“
* attributeNames: array of attributes that entities of this type have
* entityCount: number of entity instances that have this type

```bash
GET /ngsi-ld/v1/attributes
```

Will return an array of EntityAttribute Information comprising
* id: URI/name of attribute being described
* type: "EntityAttribute"
* attributeType: (whether this attribute is a Property, a GeoProperty, a Relationship, etc...)
* typeNames: array of entity types that have this attribute
* attributeCount: number of attribute instances that have this attribute


## How System vSilo Captures Data from ThingVisors
Sytem vSilo "captures" all data coming from all vThings, automatically. When it starts it asks to the SystemDB for the list of all currently existing vThings, then iterates through them to get their current data.

From then on, whenever a ThingVisor produces a "create VThing" message because it wants to instantiate a new vThing, the System vSilo intercepts it, and then it adds the corresponding vThing to itself. Thus, the System vSilo:
*  Subscribes to the internal TV/+/c_out MQTT channel, in order to grab all commands from ThingVisors
*  For each MQTT.createVThing message, it invokes an /addVThing command on the MasterController, after performing a /login as "admin"

![System vSilo architecture](Extra/vsilo_architecture.jpg)

Each newly created vThing is automatically added to the System vSilo, making its data available through the System vSilo's data broker, as seen above.

