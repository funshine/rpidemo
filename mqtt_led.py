#! /usr/bin/python3
# -*- coding: utf-8 -*-

# 引入MQTT客户端
import paho.mqtt.client as mqtt

# 引入gpiozero库
from gpiozero import LED

led = LED(17)

def init():
    led.off()
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.username_pw_set('rpi2-zerodayhong', 'rpi2rpi2')
    return client

# 设备连接上MQTT服务器时的回调函数
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    # 订阅TOPIC
    client.subscribe("rpi2-zerodayhong/led")

# 收到订阅消息时的回调函数
def on_message(client, userdata, msg):
    '''
    收到0时，关闭LED；收到1时打开LED；收到其他消息，不响应。
    '''
    print(msg.topic+" "+str(msg.payload))
    try:
        new_state = ord(msg.payload) - ord("0")
        # print(msg.payload, new_state)
        if new_state == 1 :
            # print("turn on led")
            led.on()
        elif new_state == 0 :
            # print("turn off led")
            led.off()
    except TypeError:
        print('unknown msg')

if __name__ == '__main__':
    client = init()
    client.connect("10.0.0.5")
    client.loop_forever()
