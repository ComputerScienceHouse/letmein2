#!/bin/bash
echo "Please view the README before trying to run this script"
podman run --rm -it --name=letmein-site -v ./static:/static:Z -v ./templates:/templates:Z --env-file=.env.container -p 8080:8080 letmein-site:latest
