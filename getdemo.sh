#!/bin/sh

# get demo from lan nfs
mkdir /home/pi/nfs1t && sudo mount 10.0.0.111:/nfs1t /home/pi/nfs1t/ && cd ~/nfs1t/rpi

# or get demo from github
git clone https://github.com/funshine/rpidemo && cd rpidemo