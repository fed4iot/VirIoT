FROM ubuntu:16.04

RUN apt update -y
RUN apt install -y build-essential wget
RUN apt install -y vim

COPY ./yolo-tiny /yolo

WORKDIR /yolo/

RUN wget https://pjreddie.com/media/files/yolov3-tiny.weights
#RUN wget https://pjreddie.com/media/files/yolov3.weights

RUN make -j${num_proc}

ENTRYPOINT ["./darknet","socket","cfg/yolov3-tiny.cfg","yolov3-tiny.weights"]
#ENTRYPOINT ["./darknet","socket","cfg/yolov3.cfg","yolov3.weights"]

