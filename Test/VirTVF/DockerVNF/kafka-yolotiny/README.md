# yolotiny

YOLOをsocketによるネットワークサービス拡張

YOLOが画像をsocketにより受信の待ち受け

画像を受信後、検知結果をsocketにより返信

## Parameter

TOPIC: topic name for service function chaining

## Usage

Build docker image
```bash
$docker build -t [image name] .
```

Run container
```bash
$docker run --env TOPIC=[topic name] --name [container name] -d -it [image name]
```
TOPIC = "kafka:/yolotiny/camera"

``
