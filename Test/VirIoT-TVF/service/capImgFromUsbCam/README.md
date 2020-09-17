# usbCam

## Parameter

PORT: please set port number in config.json

## Usage

Build docker image
```bash
$docker build -t [image name] .
```

Run container

example: /dev/video0

```bash
$docker run --device /dev/video0 --name [container name] -d -p PORT:PORT -it [image name]
```
## Demo

```bash
$cd demo/
$python3 client.py [output file name (.jpg)]
```

