#!/bin/bash

sudo docker run --rm -it \
    --name routines-local-cluster \
    --network="host" \
    -v /var/run/docker.sock:/var/run/docker.sock \
    -v routines-run:/mnt/routines/run \
    -v routines-data:/mnt/routines/data \
    apollodorus/routines-local-cluster:v1 
