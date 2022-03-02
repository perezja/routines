#!/bin/bash

sudo mkdir -p /mnt/routines/run /mnt/routines/data
sudo docker volume create \
  --opt type=none \
  --opt o=bind \
  --opt device=/mnt/routines/run \
  routines-run
sudo docker volume create \
  --opt type=none \
  --opt o=bind \
  --opt device=/mnt/routines/data \
  routines-data




