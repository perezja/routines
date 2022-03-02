#!/bin/bash

sudo docker run --rm -it \
    --name routines-controller \
    --network="host" \
    -e ROUTINES_APP_DIR=/mnt/routines \
    -v /var/run/docker.sock:/var/run/docker.sock \
    -v routines-run:/mnt/routines/run \
    -v routines-data:/mnt/routines/data \
    apollodorus/routines-controller:v1 
