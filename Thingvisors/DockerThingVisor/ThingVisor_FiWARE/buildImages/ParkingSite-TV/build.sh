#!/bin/bash

cd ../../
docker build -t fed4iot/fiware-parkingsite-tv -f buildImages/ParkingSite-TV/Dockerfile  ./
cd buildImages/ParkingSite-TV/