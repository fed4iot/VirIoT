# yolo-gpu

## Requirement

* Jetson Xavier 
* nvidia-container-runtime
* cuda-10.2

## Paramter

PORT: 33110

if you want to change port number for yolo-gpu,
please change the following source code:

./yolo/example/detector.c

"#define PORT 33110"

## Image build

```bash
$docker build -t [image name] .
```

## Run container

```bash
$docker run --name [container name] -it --runtime nvidia -d -p [port]:[port] [image name]
(example) $docker run --name yolo-gpu -it --runtime nvidia -d -p 33110:33110 sf/yolo-gpu
```

## Make

```bash
$cd /usr/local/bin
$ln -s ../cuda-10.2/bin/* .
$ln -s ../cuda-10.2/nvvm/bin/cicc .
$export PATH="/usr/local/cuda-10.2/bin:$PATH"
$export LD_LIBRARY_PATH="/usr/local/cuda-10.2/lib64:$LD_LIBRARY_PATH"

$cd /yolo/
$make -j8
```
## Run yolo
```bash
$./darknet socket cfg/yolov3.cfg yolov3.weights
```

## Image: kanai1192/yolo-gpu

How you run the docker image
You need to specify PATH by "--env"

PORT:33110

```bash
$docker run --name [container name] -it --env PATH=/usr/local/cuda-10.2/bin:$PATH --env LD_LIBRARY_PATH=/usr/local/cuda-10.2/lib64 -d -p [port]:[port] --runtime nvidia kanai1192/yolo-gpu
```
