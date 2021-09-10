# Generic ThingVisor

This is a demo to show the capabilities of the VirIoT platform of [Fed4IoT.org](https://fed4iot.org/) project.

## How To Run

### VirIoT Docker-base deployment

Use the following Docker command to build locally the image of the ThingVisor.

```bash
docker build -t generic-tv .
```

Use the VirIoT CLI and run the following command to add the ThingVisor to VirIoT.

```bash
python3 f4i.py add-thingvisor -i generic-tv:latest -n generic -d "generic thingVisor" -p '{}'
```

### VirIoT k8s-base deployment

Use the VirIoT CLI and run the following command to add the ThingVisor to VirIoT.

```bash
python3 f4i.py add-thingvisor -c http://$(minikube ip):$NODE_PORT -n generic -d "generic thingVisor" -y "../yaml/thingVisor-generic.yaml" -p '{"controller_url":"http://172.18.0.9:8090","tenant_id":"admin","admin_psw":"passw0rd"}'
```

Run the following command to delete the ThingVisor from VirIoT.

```bash
python3 f4i.py del-thingvisor -c http://$(minikube ip):$NODE_PORT -n generic
```

### ThingVisor parameters

When you add the ThingVisor, you can specify some parameters. Just add -p to the commandline, followed by a stringified JSON.

Currently, the Generic thingvisor accepts the following parameters:
- (mandatory) controller_url : This is the URL of the master controller.
- (mandatory) tenant_id : Username for logging in to the master controller.
- (mandatory) admin_psw : Password for logging in.

## The sample vThing

When the ThingVisor runs, it creates the sample vThing. You must add the vThing to your silo with the following command:

```bash
python3 f4i.py add-vthing -t tenant1 -s Silo1 -v generic/sample -c http://$(minikube ip):$NODE_PORT
```

This will make you be able to send command and receive command results.

## NGSI-LD data model

When the sample vThing is added to a vSilo, an NGSI-LD entity is created to the broker.

The NGSI-LD entity of sample is the following:

```json
{
 "id": "urn:ngsi-ld:generic:sample",
 "type": "Sample",
 "commands": {
  "type": "Property",
  "value": ["GENERIC_COMMAND"]
 },
 "@context": [
  "https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld"
 ]
}
```

## Sending commands to TV

For each command, the Silo controller creates the relative property on the NGSI-LD entity. In order to send a command, just modify this entity property on broker.

value must be a JSON object with the following properties:

- cmd-value : parameters of the command (mandatory)
- cmd-qos : required QoS (optional, default=0)
- cmd-id : unique command ID, e.g. start/stop (mandatory)
- cmd-nuri : alternative notification URI where to send NGSI-LD status/result (optional, default=None)

## Commands

### start
Send a sample start command. QoS must be 0 or 1.

### stop
Send a sample stop command. QoS must be 0 or 1.
