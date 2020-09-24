# tvFactory2.0

**This is development software for VirIoT ThingVisors**  
**Currently, it is WIP version and you can only use the software for testing**

## Objective

This software aims at providing dvelopment software for VirIoT ThingVisors.  
ThingVisor Factory (TVF) equips a dataflow-programming based GUI for designining ThingVisors.

## GUI Demo

This demo is extended from Node-RED.

- GUI sample image
<img src=./demo/cmia_sample.png width="450px">

## Demo for ICN/Topic-based Service Function Chaining

### Requirements

If you test ICN Service Function Chaining,  
First, cefore/cefpyco need to be installed.  
You can download cefore/cefpyco as following URL:  
https://cefore.net/

If you will use Apache Kafka, You need to delopy a kafka broker.  
Apache kafka: https://kafka.apache.org/


### Install libraries
```bash
apt install -y libgphoto2-dev
pip3 install -r requirements.txt
```

### Set parameters (Ignore)

config/nodeSetting.conifg

Please change "iface" parameter in order to satisfy your environment.  
"iface" represents the network interface that cefore will use to exchange data.

example: eth0, eth1, eno1...

### Usage

**Currently, only handle image data**

#### Publisher mode
You can publish image captured by usb camera, network camera, theta (360 degree camera)

##### network camera case
In advance, you need to set network camera and run ftp client mode.
"pubPanaCam.py" provides ftp server program.
ftp server configure is set by "config/ftpServer.json"

```bash
sudo python3 pubPanaCam.py [interet/topic name]
(example interet/topic: ccn:/camera, kafka:/camera)
```

##### usb/theta camera case
You can choose the camera which you will use in "pubImgFromUsb.py"
#DEV "USBCAM" or "THETA"

Please make sure that you need to specify the usb camera device number in "pubImgFromUsb.py"
#devID = 0 (or 1, 2, 3...)

```bash
sudo python3 pubImgFromUsb.py [interest/topic name]
(example interest/topic: ccn:/camera, kafka:/camera)
```

#### Service function mode
You can run as service function mode by using "sfNode.py"
Current available services are listed the next section.
When you run the program, you need to specify the service that you want to run
in intereset/topic name.
Interest/topic name is expressed as service function chaining manner.

```bash
sudo python3 sfNode.py [interest/topic name]
(example 1 interest/topic: ccn:/yolotinty/camera, kafka:/yolotinty/camera)
(example 2 interest/topic: ccn:/mosaic/yologpu/camera, kafka:/mosaic/yologpu/camera)
```

#### Consumer mode
You can request and receive the result by using "consumer.py" or "visualizer.py"
"consumer.py" can save the result and output file (file name: content.jpg).
"visualizer.py" can visualze the result on web brower.
**visualizer.py" requires apach server (apache2) to confirm the result.

```bash
sudo python3 consumer.py/visualizer.py [interest/topic name]
(example 1: interest/topic: ccn:/camera, kafka:/camera)
(example 2: interest/topic: ccn:/mosaic/yologpu/camera, kafka:/mosaic/yologpu/camera)
```

### Available services

**Do NOT use \_(underbar) as service name**

Defined as "config/serviceMap.json"

[lists](config/serviceMap.json)

| name | port | input | output | description |
| --- | --- | --- | --- | --- |
| yolotiny | 33101 | only content | marge | object detection (yolov3-tiny) by https://pjreddie.com/darknet/yolo/ |
| face | 33102 | only content | marge | face detection by MS FaceAPI https://azure.microsoft.com/ja-jp/services/cognitive-services/face/ |
| mosaic | 33103 | need arguments | replace | mosaic to target area |
| crop | 33104 | need arguments | replace | crop target area |
| nfov | 33105 | need arguments | replace | Equirectangular to Gnomonic projection for **360 degree image**. original is provided by https://github.com/NitishMutha/equirectangular-toolbox |
| yologpu | 33110 | only content | marge |  object detection (yolov3 with gpu) by https://pjreddie.com/darknet/yolo/ |
| yolo | 33111 | only content | marge | object detection (yolov3 w/o gpu) https://pjreddie.com/darknet/yolo/ |   
