# Jsr223 Addon
This repository contains all necessary files to run the scriptable automation PR (jsr223) (https://github.com/eclipse/smarthome/pull/1783) inside a Docker-Container. It should be no problem to run this addon outside of Docker. Simply follow the installation routine inside the Dockerfile. This image has Jython support activated.

# Requirements
- Docker
- Docker-Compose
- See the official Docker-Image for further information: https://hub.docker.com/r/openhab/openhab/

# Installation steps
- `git clone git@github.com:smerschjohann/docker-oh2-jsr223.git`
- `docker-compose build`
- start with `docker-compose up -d`
- look at it with docker-compose logs -f and tail -f run/userdata/logs/openhab.log. It should load up the oh1compat.py after around 20 seconds.
