#!/bin/sh


mkdir -p site-packages
pip3 install pymongo paho-mqtt -t site-packages

cat Dockerfile.runu | sed "s/runu-python:0.3/runu-python:0.3-linux-amd64/" | \
  docker build -f - -t thehajime/helloworld-tv-runu:1.0-linux-amd64 .
cat Dockerfile.runu | sed "s/runu-python:0.3/runu-python:0.3-linux-arm64/" | \
docker build -f - -t thehajime/helloworld-tv-runu:1.0-linux-arm64 .
cat Dockerfile.runu | sed "s/runu-python:0.3/runu-python:0.3-linux-arm/" | \
docker build -f - -t thehajime/helloworld-tv-runu:1.0-linux-arm .

docker push thehajime/helloworld-tv-runu:1.0-linux-arm
docker push thehajime/helloworld-tv-runu:1.0-linux-arm64
docker push thehajime/helloworld-tv-runu:1.0-linux-amd64

# multi-arch img
docker manifest create --amend thehajime/helloworld-tv-runu:1.0 \
	thehajime/helloworld-tv-runu:1.0-linux-arm64 \
	thehajime/helloworld-tv-runu:1.0-linux-arm \
	thehajime/helloworld-tv-runu:1.0-linux-amd64
docker manifest annotate thehajime/helloworld-tv-runu:1.0 \
	thehajime/helloworld-tv-runu:1.0-linux-arm64 --os linux --arch arm64
docker manifest annotate thehajime/helloworld-tv-runu:1.0 \
	thehajime/helloworld-tv-runu:1.0-linux-arm --os linux --arch arm
docker manifest annotate thehajime/helloworld-tv-runu:1.0 \
	thehajime/helloworld-tv-runu:1.0-linux-amd64 --os linux --arch amd64
docker manifest push --purge thehajime/helloworld-tv-runu:1.0

rm -rf site-packages
