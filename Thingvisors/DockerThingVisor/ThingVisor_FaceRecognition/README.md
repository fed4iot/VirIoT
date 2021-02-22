# FaceRecognition ThingVisor

This ThingVisor allows to do face recognition with a camera system, and to virtualize the camera system as a single face recognition device.

## How it works

First of all, the camera system must run a Python script. This script does face recognition and allows communications with the ThingVisor.

Before starting the face recognition process, you must send some pictures of the various persons to recognize (and their respective names).

The camera system will send results to ThingVisor on each status change, that is:

- when a person becomes visible to the camera and is recognized
- when a person is not visibile anymore (or is not recognized)

## How To Run

### VirIoT Docker-base deployment

Use the following Docker command to build locally the image of the ThingVisor.

```bash
docker build -t facerecognition-tv .
```

Use the VirIoT CLI and run the following command to add the ThingVisor to VirIoT.

```bash
python3 f4i.py add-thingvisor -i facerecognition-tv:latest -n facerec -d "faceRecognition thingVisor" -p '{}'
```

### VirIoT k8s-base deployment

Use the VirIoT CLI and run the following command to add the ThingVisor to VirIoT.

```bash
python3 f4i.py add-thingvisor -c http://$(minikube ip):$NODE_PORT -n facerec -d "faceRecognition thingVisor" -y "../yaml/thingVisor-faceRecognition.yaml" -p '{}'
```

Run the following command to delete the ThingVisor from VirIoT.

```bash
python3 f4i.py del-thingvisor -c http://$(minikube ip):$NODE_PORT -n facerec
```

### ThingVisor parameters

When you add the ThingVisor, you can specify some parameters. Just add -p to the commandline, followed by a stringified JSON.

Currently, the FaceRecognition thingvisor accepts the following parameters:
- (optional) camera_ip : The camera system IP.
- (optional) camera_port : The port to which the camera system running script is listening.
- (mandatory) controller_url : This is the URL of the master controller.
- (mandatory) tenant_id : Username for logging in to the master controller.
- (mandatory) admin_psw : Password for logging in.

## The detector vThing

When the ThingVisor runs, it creates the detector vThing. You must add the vThing to your silo with the following command:

```bash
python3 f4i.py add-vthing -t tenant1 -s Silo1 -v facerec/detector -c http://$(minikube ip):$NODE_PORT
```

This will make you be able to send command and receive command results.

## NGSI-LD data model

When the detector vThing is added to a vSilo, an NGSI-LD entity is created to the broker.

The NGSI-LD entity of detector is the following:

```json
{
 "id": "urn:ngsi-ld:facerec:detector",
 "type": "FaceDetector",
 "commands": {
  "type": "Property",
  "value": ["start","stop","set-face-feature","delete-by-name"]
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
Send the start command to the camera system. QoS must be 0 or 1.

### stop
Send the stop command to the camera system. QoS must be 0 or 1.

### set-face-feature
Request for sending a new picture about a specifc person. cmd-value must be an object containing the name field. QoS must be 2.

### delete-by-name
Allows to delete all the pictures associated to a given name. cmd-value must be an object containing the name field. QoS must be 0 or 1.

## Use case

The user wants to add a new picture for a person with a given name. So, it sends the set-face-feature command to the TV.

The TV sends a response to the user, that includes the URL where to patch the picture.

When the ThingVisor receives a status change from the camera system, it sends the following informations to the vSilo, through the status of the set-face-feature command:

- status (0 = person is present in the current image, 1 = not)
- name (name of the person related to status change)
- count (count of the base pictures related to the person)
- timestamp
- link_to_base_image
- link_to_current_image
