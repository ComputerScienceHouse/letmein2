#!/bin/bash

podman run --rm -it --name=lmi2-mqtt -p 1869:1869 -p 9069:9069 \
	-v ./mosquitto.conf:/mosquitto/config/mosquitto.conf:Z \
	-v ./access:/access:Z \
	eclipse-mosquitto
