#!/bin/bash

cd ../../
docker build -t fed4iot/fiware-nogreedy-tv -f buildImages/GenericNoGreedy-TV/Dockerfile  ./
cd buildImages/GenericNoGreedy-TV/