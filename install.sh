#!/bin/sh

# this is for the tf card readonly(broken), 
# everything done below will lost after reboot
sudo dpkg --configure -a
sudo apt -y --fix-broken install
sudo apt update

# install vim editor
# sudo apt -y install vim

# install mqtt lib
pip install paho-mqtt

# # ------------------Adafruit_Python_SSD1306-------------------
# # install some python lib
# sudo apt -y install build-essential python-dev python-pip
# sudo apt -y install python-imaging python-smbus

# # install lib for OLED
# mkdir ~/Projects
# cd ~/Projects
# git clone https://github.com/adafruit/Adafruit_Python_SSD1306.git
# cd Adafruit_Python_SSD1306
# sudo python setup.py install
# # --------------------------END-------------------------------

# # -----------------------luma.oled----------------------------
# install some python lib
sudo apt -y install build-essential python-dev python-pip
sudo apt -y install libfreetype6-dev libjpeg-dev python-smbus

# install lib for OLED
sudo -H pip install --upgrade pip
# sudo apt-get purge python-pip
# sudo -H pip install --upgrade luma.oled
pip install --upgrade luma.oled
pip install --upgrade luma.oled
pip install --upgrade luma.oled
# # --------------------------END-------------------------------