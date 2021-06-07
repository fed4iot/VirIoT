# FaceRecognition ThingVisor

This ThingVisor allows to do face recognition with a camera system, and to virtualize the camera system as a single face recognition device.

## How it works

The following picture shows the face recognition architecture, which comprises the Camera System, the CameraSensor ThingVisor and the FaceRecognition ThingVisor.

![Face Recognition architecture](facerec.jpg)

Overall, the Camera System sends to the CameraSensor TV every new video frame it captures from the Camera. The CameraSensor TV buffers the video frames and gives them unique identifiers. Whenever the FaceRecognition TV is ready to process a new picture, it gets it by name, asking it to the CameraSensor TV.

More specifically:

### The Camera System

- Connects to a CSI (Camera Serial Interface) Camera, via a python script. The current implementation uses CV2 to capture video from a camera attachet to a Jetson Nano board. The module responsible for video capture is called camera_mod.py (in the scripts folder of the CameraSensor TV).
- Undistorts, compresses to jpeg and scales down each video frame.
- Sends each new video frame to the CameraSensor TV via HTTP POST. The python module responsible for compression and HTTP communication is called camerasensor-to-http.py (in the scripts folder of the CameraSensor TV).
