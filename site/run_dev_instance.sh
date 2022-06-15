#!/bin/bash
echo "Please view the README before trying to run this script"
podman run --rm -it --name=letmein-site -v ./static:/static-dev:Z -v ./templates:/templates-dev:Z --env-file=.env.dev.container -p 8080:8080 letmein-site:latest
