#!/usr/bin/python3
# -*- coding: utf-8 -*-

import paho.mqtt.client as mqtt
from time import sleep
client = mqtt.Client()
client.username_pw_set('rpi2-zerodayhong', 'rpi2rpi2')
client.connect("localhost")

# 打开LED
client.publish('rpi2-zerodayhong/led', 1)

sleep(2)

# 关闭LED
client.publish('rpi2-zerodayhong/led', 0)

sleep(2)

client.publish('rpi2-zerodayhong/info', 'Info from mqtt')

while True:
    msg = raw_input('Enter info: ')
    print(msg)
    if msg == "1":
        client.publish('rpi2-zerodayhong/led', 1)
    elif  msg == "0":
        client.publish('rpi2-zerodayhong/led', 0)
    client.publish('rpi2-zerodayhong/info', msg)
