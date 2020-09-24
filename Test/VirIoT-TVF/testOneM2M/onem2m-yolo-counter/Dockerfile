#FROM ubuntu:16.04
FROM nvcr.io/nvidia/l4t-base:r32.3.1

RUN apt update -y
RUN apt install -y build-essential wget
RUN apt install -y vim
RUN apt install -y python3
#RUN apt install -y python3-pip

COPY ./src /src

WORKDIR /src/

#RUN pip3 install -r requirements.txt

RUN wget https://pjreddie.com/media/files/yolov3-tiny.weights
#RUN wget https://pjreddie.com/media/files/yolov3.weights

RUN make -j${num_proc}

ENTRYPOINT ["python3", "main.py"]
#ENTRYPOINT ["./darknet","socket","cfg/yolov3-tiny.cfg","yolov3-tiny.weights"]
#ENTRYPOINT ["./darknet","socket","cfg/yolov3.cfg","yolov3.weights"]

