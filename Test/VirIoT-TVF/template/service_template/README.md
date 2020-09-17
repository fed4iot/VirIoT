# Template

## Parameter

PORT: please set port number in config.json

## Usage

Build docker image
```bash
$docker build -t [image name] .
```

Run container
```bash
$docker run --name [container name] -d -p PORT:PORT -it [image name]
```

