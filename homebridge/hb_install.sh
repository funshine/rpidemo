#!/bin/sh

# this is for the tf card readonly(broken), 
# everything done below will lost after reboot
sudo dpkg --configure -a
sudo apt -y --fix-broken install
sudo apt update

# install some python lib
# sudo apt -y install build-essential python-dev python-pip

# Install nodejs
curl -sL https://deb.nodesource.com/setup_6.x | sudo -E bash -
sudo apt-get install -y nodejs
# remove the old version of nodejs
sudo apt autoremove -y

# use mirror
npm config set registry https://registry.npm.taobao.org

# Install Avahi and other Dependencies
sudo apt-get install -y libavahi-compat-libdnssd-dev

# Install homebridge
# sudo npm install -g homebridge
sudo npm install -g --unsafe-perm homebridge hap-nodejs node-gyp
cd /usr/lib/node_modules/homebridge/
sudo npm install --unsafe-perm bignum
cd /usr/lib/node_modules/hap-nodejs/node_modules/mdns
sudo node-gyp BUILDTYPE=Release rebuild

sudo npm install -g homebridge-blinkled

cd ~
mkdir .homebridge
# assume that rpidemo is under ~/
cp ~/rpidemo/homebridge/config.json ~/.homebridge/
# test run, use Ctrl+C to exit
homebridge


sudo cp ~/rpidemo/homebridge/homebridge /etc/default/
sudo cp ~/rpidemo/homebridge/homebridge.service /etc/systemd/system/

sudo useradd --system homebridge
# add user homebridge to group gpio
sudo adduser homebridge gpio

sudo mkdir /var/lib/homebridge
sudo cp ~/.homebridge/config.json /var/lib/homebridge/
sudo cp -r ~/.homebridge/persist /var/lib/homebridge/
sudo chmod -R 0777 /var/lib/homebridge

sudo systemctl daemon-reload
sudo systemctl enable homebridge
sudo systemctl start homebridge

systemctl status homebridge

# You can display this via systemd's journalctl
journalctl -f -u homebridge
