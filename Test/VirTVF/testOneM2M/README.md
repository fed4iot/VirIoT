# testOneM2M

## Install libraries

```bash
$sudo python3 get-pip.py
$pip3 install -r requirements.txt
```

## pubPanaCam_OneM2M.py

Publish image data to OneM2M broker 

### Setting

- FTP server for panasonic camera  
Please see the "ftpServer.json" file.  

- OneM2M Broker  
Please specify the parameters in the python code.

### Usage

```bash
$sudo python3 pubPanaCam_OneM2M.py
```

### Data mode

Example,
```
{"id": <location>:<cameraType>, 
 "type": <cameraType>, 
 "timestamp": {"type": "date time", "value": <value>}, 
 "content": {"type": "Property", "value": <b64encodeImg>}, 
 "geometry": {"type": "Point", "value": [<lat>, <long>]} 
}
```

When you retrieve data from onem2m broker,  
its data type is not "json", but "string".

## consumer.py

Simpler consumer retreives data from onem2m broker.

### Usage

```bash
$python3 consumer.py
```

## onem2m-yolo-counter

1. Retreive image data from onem2m broker  
2. Perform object detection  
3. Count number of objects (i.e., person, car,...)  
4. Perform face detection  
5. Publish the result to onem2m broker

### Usage

First you need to download model parameters  
"yolov3-tiny.weights"

```bash
$cd onem2m-yolo-counter/src/
$wget https://pjreddie.com/media/files/yolov3-tiny.weights
$python3 main.py
```

### Data mode

- YOLO

```
{"yolo": 
 [{"tagName": <object name>, "tagID": <uuid>,  
   "probability": <value>,  
   "boundingBox": ["left": <value>,  
                   "top": <value>,  
                   "width": <value>,  
                   "height": <value>]  
  ]}
}
```
- Counter

```
{"counter": {"type": "Property",  
             "target": <tag name>,  
             "value": <value>}
}
```

- Face detection

```
{"face": 
 [{"boundingBox": ["left": <value>,  
                   "top": <value>,  
                   "width": <value>,  
                   "height": <value>]  
  ]}
}
```

- Concat data
```
{"id": <location>:<cameraType>, 
 "type": <cameraType>, 
 "timestamp": {"type": "date time", "value": <value>}, 
 "content": {"type": "Property", "value": <b64encodeImg>}, 
 "geometry": {"type": "Point", "value": [<lat>, <long>]},
 "yolo": 
  [{"tagName": <object name>, "tagID": <uuid>,  
    "probability": <value>,  
    "boundingBox": ["left": <value>,  
                    "top": <value>,  
                    "width": <value>,  
                    "height": <value>]  
  ]},
  "counter": {"type": "Property",  
             "target": <tag name>,  
             "value": <value>},
  "face": 
  [{"boundingBox": ["left": <value>,  
                   "top": <value>,  
                   "width": <value>,  
                   "height": <value>]  
  ]}
}
```

## visualizer.py

1. Retreive yolo-counter result from onem2m broker
2. Require web server to visualize image

### Usage

```bash
python3 yolovisualizer.py
```
