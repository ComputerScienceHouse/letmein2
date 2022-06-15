#!/bin/bash
podman run --rm -it --name=letmein-site --env-file=.env.container -p 8080:8080 letmein-site:latest
