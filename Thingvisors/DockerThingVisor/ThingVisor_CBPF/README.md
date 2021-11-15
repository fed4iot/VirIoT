# fed4iot-cbpf

## Test Docker images as a ThingVisor

### Camera Virtualization ThingVisor

1. thingvisor: simple thingvisor for cbpf (no actuation, no logging)
2. thingvisor_w_act: thingvisor for cbpf with actuation (no logging)
3. thingvisor_w_act_logger: thingvisor for dbpf with actuation and logging (for debugging)

#### Build docker image

```bash
$cd ThingVisor_cbpf/thingvisor_w_act
$docker build -t <image name> .
```
#### Deploy VirIoT environment
First, specify docker image name in yaml  

```bash
$docker push <image name>
$python3 f4i.py add-thingvisor -c http://<master ip>:<master port> -y thingVisor-cbpf-w-act.yaml -n cbpf-vcam -d "cbpf thingvisor for camera virtualization system" -p "{'vThingName': <vThingName>, 'vThingType': <vThingType>, 'cameraEndpoint': <end_point>, 'caServer': <end_point>, 'requestRate': <request rate>}" -z <zone>
```

### Monolithic ThingVisor
```bash
$cd ThingVisor_cbpf/thingvisor_mono
$docker build -t <image name> .
```
#### Deploy VirIoT environment
First, specify docker image name in yaml  

```bash
$docker push <image name>
$python3 f4i.py add-thingvisor -c http://<master ip>:<master port> -y thingVisor-cbpf-monolithic.yaml -n cbpf -d "CBPF Monolithic ThingVisor" -p '{"pana_cam_ip": <camera ip>, "pana_cam_port": <camera port>, "AZURE_KEY": <face key>, "ENDPOINT": <face api endpoint>}'
```

## Test local environment

### Require packages
```bash
$pip3 install pillow
$pip3 install azure-cognitiveservices-vision-face
$pip3 install paho-mqtt
$pip3 install Werkzeug
$pip3 install flask
```

### Create directory
```bash
$cd v_camera_system/src/FaceDetectionAndRecognition/
$mkdir image/find_image
$mkdir image/temp_image
$mkdir cache
```

### Usage  
```bash
$cd v_camera_system/src/FaceDetectionAndRecognition  
$python3 restapi_main.py
```
### Test script (for TV side)
```bash
$cd other_tools/test_tool/
$python3 test_cbpf.py start
(start camera system)
$python3 test_cbpf.py upload 
(upload request image file to find a person)
$python3 test_cbpf.py get_result
(obtain result)
$python3 test_cbpf.py close
(end camera system)

$python3 test_cbpf.py <cmd>
 <cmd>: start, close, upload, get_result
```

## Data model
```bash
{
  "@context": {
      "type": "StructuredValue",
      "value": [
              "http://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld",
              "https://fed4iot.nz.comm.waseda.ac.jp/cbpfOntology/v1/cbpf-context.jsonld"
               ],
      "metadata": {}
  },
  "@id": "uri:ngsi-ld:CBPF:murcia:1",
  "type": "CBPF",
  "Camera": {
    "id": {
      "type": "@id",
      "value": "urn:ngsi-ld:CBPF:murcia:camera:1"
    },
    "type": {
      "type": "@id",
      "value": "camera"
    },
    "location": {
      "type": "GeoProperty",
      "value": [
        <latitude>,
        <longitude>
      ]
    },
    "createdAt": {
      "type": "Property",
      "value": <datetime>
    },
    "dataProvider": {
      "type": "Property",
      "value": <value>
    },
    "entityVesrion": {
      "type": "Property",
      "value": "1.0"
    },
    "deviceModel": {
      "type": "Relationship",
      "value": <device model>
    },
    "description": {
      "type": "Property",
      "value": "panasonic network camera"
    },
    "FileName": {
      "type": "Property",
      "value": <file name>
    }
  }
}
```

## other codes

1. v_camera_system: virtual camera system for detecting human using FaceAPI and Panasonic camera
2. py_face_rec: python codes for detecting human using https://github.com/ageitgey/face_recognition
3. other useful tools
