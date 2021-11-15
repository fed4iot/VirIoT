# Cross Boarder Person Finder ThingVisor (Monolithic version)

This ThingVisor connect to a camera accessible through an IP address using openCV and finds a face in the pictures taken by the camera.  The ThingVisor receives the face to be detected through a command.  This implementation provides face detection, feature extraction, and feature matching capabilities while using feature extraction and feature matching functions of Azure Face API.  Users of this ThingVisor needs to have access to Azure Face API.

## How to Run

### Local Docker deployment

Use the VirIoT CLI and execute the following command. The <font color="Red">IP address and port number</font> of a camera and also the <font color="Red">key to access Azure Face API</font> must be provided as the parameter.

```bash
python3 f4i.py add-thingvisor -c  -i fed4iot/cbpf-monolithic-tv -n cbpf -p '{"pana_cam_ip": "[camera IP address]", "pana_cam_port": "[camera port", "AZURE_KEY": "[Azure key]"}' -d "CBPF ThingVisor"
```

### Kubernetes deployment

```bash
python3 f4i.py add-thingvisor -c http://[k8s_node_ip]:[NodePort] -n cbpf -p '{"pana_cam_ip": "[camera IP address]", "pana_cam_port": "[camera port", "AZURE_KEY": "[Azure key]"}' -d "CBPF ThingVisor" -y "../yaml/thingVisor-cbpf-monolithic.yaml"
```

## NGSI-LD data model

The status of person finding is expressed by the following NGSI-LD entity:

```
{
    "id": "urn:ngsi-ld:CPBF:detector",
    "type": "CBPF Event",
    "location": {,
        "type": "Property",
        "value": [<latitude>,<longitude>]
    },
    "source": {
        "type": "Property",
        "value": "<camera URL>"
    },
    "dataProvider": {
        "type": "Property",
        "value": "<image file URL>"
    },
    "entityVersion": {
        "type": "Property",
        "value": "<camera version>"
    },
    "description": {
        "type": "Property",
        "value": "vertual person finder"
    },
    "softwareVersion": {
        "type": "Property",
        "value": "1.0"
    },
    "DetectHuman": {
        "type": "Property",
        "value": true
    }
}
```