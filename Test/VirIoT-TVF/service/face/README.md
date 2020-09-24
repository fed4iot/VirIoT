# face

## Parameter

PORT: 33102

## Usage

Build docker image
```bash
$docker build -t [image name] .
```

Run container
```bash
$docker run --name [container name] -d -p 33102:33102 -it [image name]
```

## Demo

```bash
$python3 client.py lena.jpg
```
