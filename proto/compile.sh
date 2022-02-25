#!/bin/bash

../env/bin/python3 -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. routine.proto
