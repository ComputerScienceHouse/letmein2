#!/bin/bash
podman run --rm -it --name=letmein-site -v ./static:/static -v ./templates:/templates -p 8080:8080 letmein-site:latest