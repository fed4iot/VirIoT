# yolov3tiny with gpu on Jetson Nano

## Requirements
- Jetson Nano (JetPack 4.9)
- nvidia-container-runtime
- cuda-10.2

## Description

subscribe to kafka broker  
once receive iamge, then object detection is peformed  
and publish result to kafka broker 

## Pull image

```bash
$docker pull kanai1192/kafka-yolotiny-jetnano
```
## Instantiate container

```bash
$docker run --name [container name] -v /usr/local/cuda-10.2/:/usr/local/cuda-10.0/ --env TOPIC=[topic name] -d -it kanai1192/kafka-yolotiny-jetnano
```
- Example of topic name
[topic name] = "kafka:/yolotiny/camera"

## My personal memo

### Parameter

PORT: 33101

### Usage

Build docker image
- first use Dockerfile
- next use Dockerfile2

```bash
$docker build -t [image name] .
```

Run container
```bash
$docker run --name [container name] --runtime nvidia -d -it [image name]
```

### Demo

Send a test image to yolo and receive result 

```bash
$cd demo/
$python3 client.py
```
