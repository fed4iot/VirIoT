# yolo

YOLOをsocketによるネットワークサービス拡張

YOLOが画像をsocketにより受信の待ち受け

画像を受信後、検知結果をsocketにより返信

## Parameter

PORT: 33101

## Usage

Build docker image
```bash
$docker build -t [image name] .
```

Run container
```bash
$docker run --name [container name] -d -p 33101:33101 -it [image name]
```

## Demo

Send a test image to yolo and receive result 

```bash
$cd demo/
$python3 client.py
```
