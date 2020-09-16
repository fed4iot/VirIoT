#FROM ubuntu:16.04
FROM nvcr.io/nvidia/l4t-base:r32.3.1

RUN apt update -y
RUN apt install -y build-essential wget
RUN apt install -y vim
RUN apt install -y python3-pip

#WORKDIR /usr/local/bin

#RUN ["ln", "-s", "../cuda-10.2/bin/*", "."]
#RUN ["ln", "-s", "../cuda-10.2/nvvm/bin/cicc", "."]

COPY ./src /src

WORKDIR /src/

RUN wget https://pjreddie.com/media/files/yolov3-tiny.weights
#RUN wget https://pjreddie.com/media/files/yolov3.weights
RUN pip3 install -r requirements.txt

#ENV export PATH="/usr/local/cuda-10.2/bin:$PATH"
#ENV export LD_LIBRARY_PATH="/usr/local/cuda-10.2/lib64:$LD_LIBRARY_PATH"

#RUN make -j${num_proc}

#ENTRYPOINT ["./darknet","socket","cfg/yolov3-tiny.cfg","yolov3-tiny.weights"]
#ENTRYPOINT ["./darknet","socket","cfg/yolov3.cfg","yolov3.weights"]

