# yolov3 with gpu on xavier

## Requirements
- Jetson Xavier (JetPack 4.9)
- nvidia-container-runtime
- cuda-10.2

## Description

subscribe to kafka broker  
once receive iamge, then object detection is peformed  
and publish result to kafka broker 

## Pull image

```bash
$docker pull kanai1192/kafka-yologpu-xavier
```
## Instantiate container

```bash
$docker run --name [container name] -v /usr/local/cuda-10.2/:/usr/local/cuda-10.0/ --env TOPIC=[topic name] -d -it kanai1192/kafka-yologpu-xavier
```
- Example of topic name
[topic name] = "kafka:/yologpu/camera"

## My personal memo

### Parameter

PORT: 33110

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
