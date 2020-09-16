# cv2face

face detection by using cascade classifier (provided by opencv)

## Parameter

TOPIC: topic name for service function chaining

## Usage

Build docker image
```bash
$docker build -t [image name] .
```

Run container
```bash
$docker run --name [container name] --env TOPIC=[topic name] --env SERVICE=[service name] -d -it [image name]
```
