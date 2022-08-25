#!/bin/bash
set -e
cd .. # Hack to make OKDeez happy
podman build ./site/ --tag=letmein-site
