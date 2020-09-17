# yolo

YOLOをsocketによるネットワークサービス拡張

YOLOが画像をsocketにより受信の待ち受け

画像を受信後、検知結果をsocketにより返信

## Parameter

PORT: 33111

## Usage

Build docker image
```bash
$docker build -t [image name] .
```

Run container
```bash
$docker run --name [container name] -d -p 33111:33111 -it [image name]
```

## Demo

Send a test image to yolo and receive result 

```bash
$cd demo/
$python3 client.py
```
## Performance

yolo does not run on the GPU machine.
because include yolov3.weight (full spec),
it takes several seconds (50 sec) to run.
