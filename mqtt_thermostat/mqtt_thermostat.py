#! /usr/bin/python3
# -*- coding: utf-8 -*-

import time
import json
from pprint import pprint
# 引入MQTT客户端
import paho.mqtt.client as mqtt

thermostats = ["thermostat_diningroom", "thermostat_livingroom", "thermostat_studyroom", "thermostat_master_bedroom", "thermostat_secondary_bedroom"]

thermostat_accessorys = {
    "name": "thermostat_livingroom",
    "service_name": "客厅温控器",
    "service": "Thermostat"
}

def on_message_from_get(client, userdata, msg):
    """
    处理来自TOPIC homebridge/from/get 的信息
    
    """
    print(msg.topic + ' : ' + msg.payload)
    message = json.loads(msg.payload)
    print(json.dumps(message, indent=4, sort_keys=True))
    print(message.items())
    try:
        pass
    except TypeError:
        print('unknown msg in topic homebridge/from/get')

def on_message_from_set(client, userdata, msg):
    """
    处理来自TOPIC homebridge/from/set 的信息
    
    """
    print(msg.topic + ' : ' + msg.payload)
    message = json.loads(msg.payload)
    print(json.dumps(message, indent=4, sort_keys=True))
    print(message.items())
    try:
        pass
    except TypeError:
        print('unknown msg in topic homebridge/from/set')

def on_message_from_response(client, userdata, msg):
    """
    处理来自TOPIC homebridge/from/response 的信息
    
    """
    print(msg.topic + ' : ' + msg.payload)
    message = json.loads(msg.payload)
    print(json.dumps(message, indent=4, sort_keys=True))
    print(message.items())
    for ts in thermostats:
        if ts in message:
            print(ts + " exists")
        else:
            print("add " + ts + " to home")
    try:
        pass
    except TypeError:
        print('unknown msg in topic homebridge/from/response')


def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    # 订阅所有TOPIC
    client.subscribe("homebridge/#")

    get_accessorys(client)

def on_message(client, userdata, msg):
    print(msg.topic + " " + str(msg.payload))

def get_accessorys(client):
    """
    topic: homebridge/to/get
    payload: {"name": "*"}
    """
    payload = '{"name": "*"}'
    client.publish("homebridge/to/get", payload)


def init():
    client = mqtt.Client()
    client.message_callback_add("homebridge/from/get", on_message_from_get)
    client.message_callback_add("homebridge/from/set", on_message_from_set)
    client.message_callback_add("homebridge/from/response", on_message_from_response)
    client.on_connect = on_connect
    client.on_message = on_message
    client.username_pw_set('rpi2-zerodayhong', 'rpi2rpi2')
    client.reconnect_delay_set()
    return client


if __name__ == '__main__':
    try:
        client = init()
        client.connect("10.0.0.5")
        client.loop_forever()
    finally:
        client.disconnect()
