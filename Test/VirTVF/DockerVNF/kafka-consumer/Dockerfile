FROM python:3.6.9-slim

RUN apt update -y
#RUN apt install -y build-essential wget
RUN apt install -y vim
#RUN apt install -y python3
#RUN apt install -y python3-pip

RUN pip install kafka-python

COPY ./src /src

WORKDIR /src/

#RUN wget https://pjreddie.com/media/files/yolov3-tiny.weights
#RUN wget https://pjreddie.com/media/files/yolov3.weights

#RUN make -j${num_proc}

#ENTRYPOINT ["./darknet","socket","cfg/yolov3-tiny.cfg","yolov3-tiny.weights"]
#ENTRYPOINT ["./darknet","socket","cfg/yolov3.cfg","yolov3.weights"]

