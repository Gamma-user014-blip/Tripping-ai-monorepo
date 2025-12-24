#!/bin/bash
ls shared/data_types/*.proto | xargs -I {} protoc --proto_path=. --python_out=. {}