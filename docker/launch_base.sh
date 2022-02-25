#!/bin/bash

sudo docker run --rm -it \
    --network="host" \
    -e ROUTINES_APP_DIR=/tmp/routines \
    -v /var/run/docker.sock:/var/run/docker.sock \
    -v /tmp/routines:/tmp/routines \
    -v /Users/James/work/routines/:/Users/James/work/routines \
    -w /Users/James/work/routines/routines \
    apollodorus/routines-base:v1 \
    /bin/bash
