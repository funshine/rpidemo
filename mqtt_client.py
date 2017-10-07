#! /usr/bin/python3
# -*- coding: utf-8 -*-

# 引入MQTT客户端
import paho.mqtt.client as mqtt

# # 引入gpiozero库
# from gpiozero import LED

import RPi.GPIO as GPIO
class LED:
    def __init__(self, pin):
        self.pin = pin
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pin, GPIO.OUT)
        GPIO.output(self.pin, GPIO.LOW)
    def on(self):
        GPIO.output(self.pin, GPIO.HIGH)
    def off(self):
        GPIO.output(self.pin, GPIO.LOW)
    def close(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pin, GPIO.IN)

led = LED(17)
info = "mqtt"

# 设备连接上MQTT服务器时的回调函数
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    # 订阅TOPIC
    client.subscribe("rpi2-zerodayhong/#")
    # client.subscribe("rpi2-zerodayhong/led")

def on_message_led(client, userdata, msg):
    """
    处理来自TOPIC led的信息
    收到0时，关闭LED；收到1时打开LED；收到其他消息，不响应。
    """
    # print(msg.payload)
    try:
        # new_state = ord(msg.payload) - ord("0")
        new_state = int(msg.payload)
        # print(msg.payload, new_state)
        if new_state == 1 :
            # print("turn on led")
            led.on()
        elif new_state == 0 :
            # print("turn off led")
            led.off()
    except TypeError:
        print('unknown msg in topic led')

def on_message_info(client, userdata, msg):
    """
    处理来自TOPIC info的信息
    """
    global info
    # print(msg.payload)
    try:
        # send msg to display module
        if len(msg.payload) > 19:
            print(msg.payload[:19])
            info = msg.payload[:19]
        else:
            print(msg.payload)
            info = msg.payload[:]
    except TypeError:
        print('unknown msg in topic info')

# 收到订阅消息时的回调函数
def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))

def init():
    led.off()
    client = mqtt.Client()
    client.message_callback_add("rpi2-zerodayhong/led", on_message_led)
    client.message_callback_add("rpi2-zerodayhong/info", on_message_info)
    client.on_connect = on_connect
    client.on_message = on_message
    client.username_pw_set('rpi2-zerodayhong', 'rpi2rpi2')
    return client

if __name__ == '__main__':
    try:
        client = init()
        client.connect("10.0.0.5")
        client.loop_forever()
    finally:
        led.close()
        client.disconnect()
