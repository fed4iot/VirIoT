# FaceRecognition ThingVisor

This ThingVisor allows to do face recognition with a camera system, and to virtualize the camera system as a single face recognition device.

## How it works

The following picture shows the face recognition architecture, which comprises the Camera System, the CameraSensor ThingVisor and the FaceRecognition ThingVisor.

Overall, the Camera System sends to the CameraSensor TV every new video frame it captures from the Camera. The CameraSensor TV buffers the video frames and gives them unique identifiers. Whenever the FaceRecognition TV is ready to process a new video frame, it gets it by name, asking it to the CameraSensor TV. The FaceRecognition TV processes the frame by comparing it to a target picture of a person. If a match is found, an event is sent from the FaceRecognition TV to a vSilo (that hosts the IoT Broker and talks to an external Application).

Users do not interact directly with the FaceRecognition ThingVisor. The whole process is driven via the User's vSilo, instead, as usual in VirIoT. Users POST target faces (to be matched) to the HTTP Broker running inside the vSilo. Moreover, they can act (using the usual VirIoT's actuation workflow) upon the face recognition process by starting (or deleting) a specific job recognition process, identifying it by name (of a target person, for example, or whatever name they assign to the job, "Andrea" in the picture below).

![Face Recognition architecture](facerec.jpg)

The purpose of having the CameraSensor ThingVisor in between the Camera System and the FaceRecognition is that, in principle, several different ThingVisors, performing diverse tasks such as face recognition, object recognition, motion detection, etc..., can attach to the CameraSensor ThingVisor. They will act as downstream processors, each fetching a copy of the same video frame for different purposes. This avoids each processor fetching a separate copy of the current video frame from the Camera System, thus avoiding redundant network traffic from the Root Data Domain (where the Camera System lives) into VirIoT. Moreover, VirIoT's HTTP Data Distribution System is operating in between the upstream CameraSensor and the downstream ThingVisors, transparently caching all HTTP requests and responses, so that ThingVisors (and vSilos) that are requesting the same picture (by id) from the CameraSensor, will efficiently get it from the closest proxy.

More specifically:

### The Camera System

- Connects to a CSI (Camera Serial Interface) Camera. The current implementation uses CV2 to capture video from a camera attached to a Jetson Nano board. 
- Undistorts, compresses to jpeg, and scales down each video frame.
- Sends each new video frame to the CameraSensor TV via an HTTP POST request to the TV's ``/framesinput`` API.

The Camera System is currently implemented as a python script responsible for compression and HTTP communication, which is called [camerasensor-to-http.py](../ThingVisor_CameraSensor/jetbot_scripts/camerasensor-to-http.py). It, in turn, imports a python module, which is responsible for video capture, and is called [camera_mod.py](../ThingVisor_CameraSensor/jetbot_scripts/camera_mod.py). Both can be found in the scripts folder of the CameraSensor TV.

### The CameraSensor ThingVisor
- Offers a REST interface to receive video frames, via HTTP POST.

  The interface is called ``/framesinput`` and accepts multipart POST requests composed of 2 parts:
  - a part named ``file`` that is a jpeg file representing the current video frame
  - a part named ``json`` that is a json file representing the timestamp when the video frame was captured, in the following form: ``{"observedAt":STRING}``

  The REST API lives at ip port 5000, so if, for instance, <CAMERASENSORTV_PUBLIC_IP> is the public ip address to reach the CameraSensor TV and <PORT_MAPPED_TO_5000> is the external port mapped onto internal port 5000, the following ``echo`` and ``curl`` command sequence is an example to POST a new video frame:
  ```bash
  $ echo {\"observedAt\":\"02-02-2021 14:34\"} > metadata.json
  $ curl -F "file=@currentframe.jpg" -F "json=@metadata.json" http://<CAMERASENSORTV_PUBLIC_IP>:<PORT_MAPPED_TO_5000>/framesinput
  ```
- Buffers a certain (configurabile) amount of video frames, FIFO style, and it gives unique identifiers to them, upon arrival of each new frame. It buffers the jpeg compressed pictures in memory.
  
  The size of the buffer is a configurabile parameter of the ThingVisor, named ``buffersize``. The default size of the video buffer is ``20``. It can be specified at creation time, when the TV is added to VirIoT, as in the following example, where a TV is added using the yaml that specifies a CameraSensor, the name "camerasensor-tv" is given to it, and the ``buffersize`` parameter is set to ``30``.

  ```bash
  $ f4i.py add-thingvisor -y ../yaml/thingVisor-cameraSensor-http.yaml -n camerasensor-tv -d "camera frames via http" -p '{"buffersize":30}' -z default
  ```

  Alternatively, by using the update-thingvisor VirIoT command on a running instance of the TV, the ``buffersize`` parameter can be changed in real-time, as follows:

  ```bash
  $ f4i.py update-thingvisor -n camerasensor-tv -p '{"buffersize":40}'
  ```

- Offers a single vThing, named "sensor". This vThing, upon arrival of each new frame, emits an event representing context information about the received video frame, in the form of a NGSI-LD Entity containing the picture's identifier.

  The NGSI-LD Entity emitted at each frame arrival is represented in NGSI-LD "neutral format" (assuming the ThingVisor's name is "camerasensor-tv") by entity of type "NewFrameEvent". It has just one Property, named "frameIdentifier". The information about the timestamp of the video frame is dropped, as of now, since it is not needed for face recognition purposes. Here follows an example:
  ```
  {
    id : urn:ngsi-ld:camerasensor-tv:sensor
    type : NewFrameEvent
    frameIdentifier : {
      type : Property
      value : "1623229264110-0"
    }
  }
  ```

- Offers a REST interface to fetch a specific frame by its identier, via HTTP GET.

  The interface is called ```/currentframe/<randomid>``` and accepts GET HTTP requests. It gives back data with mime-type "image/jpeg".

  The following ``curl`` command is an example to GET video frame by its id:
  ```bash
  $ curl --output videoframe.jpg http://<CAMERASENSORTV_PUBLIC_IP>:<PORT_MAPPED_TO_5000>/currentframe/1623229264110-0
  ```

### The FaceRecognition ThingVisor
- It is designed so that it "chains" to an upstream "sensor" vThing implemented by a CameraSensor ThingVisor: upon chaining, it subscribes to Entities coming from the upstream CameraSensor's "sensor" vThing. Such Entities convey the identifiers of a stream of video frames buffered by the CameraSensor. FaceRecognition GETs the new frames at its convenience (thus operating at its own framerate, ususally different than the framerate the video frames are produced by the Camera System).

  The rate that FaceRecognition uses to get frames from CameraSensor is a configurabile parameter of the TV, named ``fps``. Its default value is ``2``.

  The name of the upstream vThing to chain to is a configurabile parameter as well, named ``upstream_vthingid``. By default, at startup, if no upstream vThing of a CameraSensor is specified, the FaceRecognition TV sits idle, waiting for an update command to specify it.

  Both parameters can be specified at creation time, when the TV is added to VirIoT, as in the following example, where a TV is added using the yaml that specifies a FaceRecognition, the name "facerecognition-tv" is given to it, the ``upstream_vthingid`` parameter is set to ``camerasensor-tv/sensor`` (as it represents a vThing identifier, which in VirIoT is composed of ThingVisorName/vThingName), and the ``fps`` parameter is set to ``12``.

  ```bash
  $ f4i.py add-thingvisor -y ../yaml/thingVisor-faceRecognition.yaml -n "facerecognition-tv" -d "recognizes faces" -p '{"fps":12, "upstream_vthingid":"camerasensor-tv/sensor"}' -z default
  ```

  Alternatively, by using the update-thingvisor VirIoT command on a running instance of the TV, both parameters (either one-by-one or together) can be changed in real-time, as follows:

  ```bash
  $ f4i.py update-thingvisor -n facerecognition-tv -p '{"upstream_vthingid":"camerasensor-tv/sensor"}'
  $ f4i.py update-thingvisor -n facerecognition-tv -p '{"fps":6}'
  ```

- Offers a single vThing, named "detector". The "detector" vThing does not produce any information (in the form of NGSI-LD Entities) on its own. Thus, it is not a sensor, rather an actuator. Specifically, it represents an actuator that is activated by users via ``startjob`` commands, that need to have a QoS of 2, meaning the command does not terminate immediately with a given result, but status of the command is going to be continuously updated by the actuator. The job is given a name by the user, and the ``startjob`` command is issued to the actuator. Once the job is started via its command, the "detector" updates the command status whenever a matching face is detected. The updated status embeds links to the video frame that matched, to the original picture of the face, and to the corresponding job's name. Thus, several jobs can be started and the status queue will receive a stream of updates (each possibly overwriting the previous update, depending on the specific IoT Broker that receives the updates).

  In parallel and asynchronously to starting jobs, users have to POST target pictures of faces they want to be recognized. Such target pictures are POSTed under a given name that has to match the name of a corresponding job. Pictures can be POSTed without a corresponding job being started yet; a job can be started without targets. As soon as both a job and target pictures, with the same name, are present in the "detector", it starts sending back updates to the ``startjob`` command status.

  More specifically, the "detector" vThing implemented by the FaceRecognition TV offers two commands:

  - ``startjob`` command.

  An example JSON object to send to the ``startjob`` command:
  ```
  {"cmd-id":"xaxaxa","cmd-qos":2,"cmd-value":{"job":"123456"}}
  ```
  - ``deletejob`` command, that is used to remove all pictures for a given job name, and to stop the corresponding recognition process.

  Thus, the "detector" vThing, being an actuator only, is represented by an NGSI-LD Entity having just properties that are related to the above commands. Its id is "urn:ngsi-ld:facerecognition-tv:detector" (assuming the ThingVisor is named "facerecognition-tv"), and its type is "FaceRecognitionEvent". Here follows an example:
```
{
  "id": "urn:ngsi-ld:facerecognition-tv:detector",
  "type": "FaceRecognitionEvent",
  "commands": {
    "value": [
      "startjob",
      "deletejob"
    ],
    "type": "Property"
  },
  "startjob": {
    "value": {
      "cmd-id": "xaxaxa",
      "cmd-qos": 2,
      "cmd-value": {
        "job": "123456"
      }
    },
    "type": "Property"
  },
  "startjob-status": {
    "value": {
      "cmd-id": "xaxaxa",
      "cmd-nuri": "viriot://vSilo/tenant1_silongsildorionld1-eu/data_in",
      "cmd-qos": 2,
      "cmd-value": {
        "job": "123456"
      },
      "cmd-status": {
        "job": "123456",
        "name": "pippo",
        "original-uri": "/media/60ba4b6a5faca138c398b3d4",
        "recognized-uri": "media/60ba4b7b5faca138c398b3e8"
      }
    },
    "type": "Property"
  },
  "startjob-result": {
    "value": {},
    "type": "Property"
  },
  "deletejob": {
    "value": {},
    "type": "Property"
  },
  "deletejob-status": {
    "value": {},
    "type": "Property"
  },
  "deletejob-result": {
    "value": {},
    "type": "Property"
  }
}
```

- Offers a REST interface to insert target pictures by their job identifer and person name, via HTTP POST, and to retrieve information about them, via HTTP GET.

- Offers a REST interface to fetch pictures their identier, via HTTP GET.


### The vSilo
- Target pictures of faces to be matched against the incoming video frames are POSTed by Users to the vSilo's HTTP Broker. The HTTP Broker running inside the vSilo acts as a proxy to the HTTP REST interface offered by the FaceRecognition ThingVisor, which is not intended for direct access from Users. Thus the vSilo's HTTP Broker acts as the only entry point for Users (and Applications) to the face recognition process.

## How to run it

### Running the Camera System

### Running the CameraSensor ThingVisor
Set endpoint to make the HTTP Data Distribution able to proxy the /framesinput and /currentframe APIs. This way, the FaceRecognition TV (and other ThingVisors as well) can GET video frames using the CameraSensor's service name, globally within VirIoT, exploiting efficien caching and mukticast distribution of the video frames.

### Running the FaceRecognition ThingVisor
Set endpoint to make the HTTP Data Distribution able to proxy the /targetfaces and /recognizedfaces APIs.

### Adding and using the "detector" vThing in vSilo
