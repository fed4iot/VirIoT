 # specify the node base image with your desired version node:<version>

FROM python:3.6-slim

RUN apt-get update
RUN apt-get -y install screen 

# for face recognition
RUN apt-get install -y --fix-missing \
#    build-essential \
#    cmake \
#    gfortran \
#    git \
#    wget \
#    curl \
#    graphicsmagick \
#    libgraphicsmagick1-dev \
#    libatlas-base-dev \
#    libavcodec-dev \
#    libavformat-dev \
#    libgtk2.0-dev \
#    libjpeg-dev \
#    liblapack-dev \
#    libswscale-dev \
#    pkg-config \
#    python3-dev \
#    python3-numpy \
     libopencv-dev \
#    software-properties-common \
    zip \
    && apt-get clean && rm -rf /tmp/* /var/tmp/*

#RUN cd ~ && \
#    mkdir -p dlib && \
#    git clone -b 'v19.9' --single-branch https://github.com/davisking/dlib.git dlib/ && \
#    cd  dlib/ && \
#    python3 setup.py install --yes USE_AVX_INSTRUCTIONS
# end face recognition

COPY app/ /app
WORKDIR /app
RUN pip3 install -r requirements.txt

ENTRYPOINT []

CMD [ "/bin/bash", "./start.sh" ]

EXPOSE 5000
