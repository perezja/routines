#!/bin/bash

sudo docker run --rm -it \
    --name routines-base \
    --network="host" \
    -e ROUTINES_APP_DIR=/mnt/routines \
    -v routines-run:/mnt/routines/run \
    -v routines-data:/mnt/routines/data \
    -v /home/$USER/projects/routines:/usr/local/share/routines \
    -w /usr/local/share/routines \
    apollodorus/routines-base:v1 \
   /bin/bash 
