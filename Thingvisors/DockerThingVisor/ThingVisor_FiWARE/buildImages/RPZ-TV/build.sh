#!/bin/bash

cd ../../
docker build -t fed4iot/fiware-rpz-tv -f buildImages/RPZ-TV/Dockerfile  ./
cd buildImages/RPZ-TV/