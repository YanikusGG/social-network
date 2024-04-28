#!/bin/bash

python3 -m grpc_tools.protoc -I./lib/proto/ --python_out=. --pyi_out=. --grpc_python_out=. ./lib/proto/social_engine.proto
