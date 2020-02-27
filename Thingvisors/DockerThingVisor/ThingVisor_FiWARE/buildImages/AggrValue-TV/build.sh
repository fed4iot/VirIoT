#!/bin/bash

cd ../../
docker build -t fed4iot/fiware-aggrvalue-tv -f buildImages/AggrValue-TV/Dockerfile  ./
cd buildImages/AggrValue-TV/