#!/bin/bash

cd ../../
docker build -t fed4iot/fiware-greedy-tv -f buildImages/greedy-TV/Dockerfile  ./
cd buildImages/greedy-TV/
