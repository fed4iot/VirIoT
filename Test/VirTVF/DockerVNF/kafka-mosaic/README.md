# mosaic

mosaic to detected areas

## Parameter

TOPIC: topic name for service function chaining
SERVICE: target service name
TAG: target tag name

## Usage

Build docker image
```bash
$docker build -t [image name] .
```

Run container
```bash
$docker run --name [container name] --env TOPIC=[topic name] --env SERVICE=[service name] --env TAG=[tag name] -d -it [image name]
```
