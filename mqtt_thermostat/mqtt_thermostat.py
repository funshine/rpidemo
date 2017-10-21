#! /usr/bin/python3
# -*- coding: utf-8 -*-

import time
import json
import struct
# 引入MQTT客户端
import paho.mqtt.client as mqtt
import crc


class ThermostatMQTTClient(mqtt.Client):
    def __init__(self):
        mqtt.Client.__init__(self)
        self.thermostat_names = ["thermostat_diningroom", "thermostat_livingroom",
                                 "thermostat_studyroom", "thermostat_master_bedroom", "thermostat_secondary_bedroom"]

        self.thermostat_accessories = {
            "thermostat_diningroom": {
                "name": "thermostat_diningroom",
                "service_name": "餐厅温度",
                "service": "Thermostat",
                "TargetTemperature": {"minValue":5, "maxValue": 35, "minStep": 1}
            },
            "thermostat_livingroom": {
                "name": "thermostat_livingroom",
                "service_name": "客厅温度",
                "service": "Thermostat",
                "TargetTemperature": {"minValue":5, "maxValue": 35, "minStep": 1}
            },
            "thermostat_studyroom": {
                "name": "thermostat_studyroom",
                "service_name": "书房温度",
                "service": "Thermostat",
                "TargetTemperature": {"minValue":5, "maxValue": 35, "minStep": 1}
            },
            "thermostat_master_bedroom": {
                "name": "thermostat_master_bedroom",
                "service_name": "主卧温度",
                "service": "Thermostat",
                "TargetTemperature": {"minValue":5, "maxValue": 35, "minStep": 1}
            },
            "thermostat_secondary_bedroom": {
                "name": "thermostat_secondary_bedroom",
                "service_name": "次卧温度",
                "service": "Thermostat",
                "TargetTemperature": {"minValue":5, "maxValue": 35, "minStep": 1}
            }
        }

        self.thermostat_manufacturer = "zeroday"
        self.thermostat_model = "rpi1b"
        self.thermostat_firmwareversion = "0.0.2"
        self.thermostat_info = {
            "thermostat_diningroom": {
                "addr": 1,
                "serialnumber": 5001
            },
            "thermostat_livingroom": {
                "addr": 2,
                "serialnumber": 5002
            },
            "thermostat_studyroom": {
                "addr": 3,
                "serialnumber": 5003
            },
            "thermostat_master_bedroom": {
                "addr": 4,
                "serialnumber": 5004
            },
            "thermostat_secondary_bedroom": {
                "addr": 5,
                "serialnumber": 5005
            }
        }

    def remove_accessories(self):
        """
        topic: homebridge/to/remove
        payload: {"name": "thermostat_livingroom"}
        """
        for th in self.thermostat_names:
            info = {
                "name": th
            }
            # print(info)
            payload = json.dumps(info)
            self.publish("homebridge/to/remove", payload)

    def add_accessory(self, accessory):
        """
        add accessory, pub
        topic: homebridge/to/add
        payload: {"name": "thermostat_livingroom", "service_name": "客厅温控器", "service": "Thermostat"}
        """
        payload = json.dumps(self.thermostat_accessories[accessory])
        self.publish("homebridge/to/add", payload)

    def get_accessories(self):
        """
        topic: homebridge/to/get
        payload: {"name": "*"}
        """
        payload = '{"name": "*"}'
        # self.message_callback_add("homebridge/from/response", self.on_message_from_response)
        self.publish("homebridge/to/get", payload)

    def set_accessory_info(self):
        """
        topic: homebridge/to/set/accessoryinformation
        payload: {"name": "thermostat_livingroom", "manufacturer": "zeroday", "model": "rpi1b", "serialnumber": "5002", "firmwarerevision": "0.0.2"}
        """
        for th in self.thermostat_names:
            info = {
                "name": th,
                "manufacturer": self.thermostat_manufacturer,
                "model": self.thermostat_model,
                "serialnumber": self.thermostat_info[th]["serialnumber"],
                "firmwareversion": self.thermostat_firmwareversion
            }
            # print(info)
            payload = json.dumps(info)
            self.publish("homebridge/to/set/accessoryinformation", payload)

    def set_accessory(self, addr, characteristic, value):
        """
        topic: homebridge/to/set
        payload: {"name": "thermostat_livingroom", "service_name": "客厅温控器", "characteristic": "CurrentTemperature", "value": 20}
        """
        for k, v in self.thermostat_info.items():
            if addr == v["addr"]:
                data = self.thermostat_accessories[k].copy()
                data.pop('TargetTemperature', None)
                data["characteristic"] = characteristic
                data["value"] = value
                payload = json.dumps(data)
                # print(payload)
                self.publish("homebridge/to/set", payload)

    def parse(self, data):
        if data is None:
            return None
        datalen = len(data)
        if datalen < 8:
            return None
        header = data[:8]
        status = struct.unpack('1B', data[0:1])[0]
        my_id = struct.unpack('3B', data[1:4])
        userid = (my_id[0] << 16) + (my_id[1] << 8) + (my_id[2])
        num = struct.unpack('1B', data[4:5])[0]
        addr = struct.unpack('1B', data[5:6])[0]
        l = struct.unpack('2B', data[6:8])
        length = (l[0] << 8) + (l[1])
        # print("Status: {0}".format(status))
        # print("Userid: {0}".format(userid))
        # print("Panel Number: {0}".format(num))
        # print("Device Addr: {0}".format(addr))
        # print("Pack Length: {0}".format(length))

        if datalen != length:
            print("Data length mismatch")
            return None
        if datalen != 8 + 7 * num:
            print("Panel Number mismatch data length")
            return None
        if num == 0:
            print("Data has no panel info")
            return None
        start = 8
        for i in range(0, num):
            pdata = data[start:start + 7]
            self.parsepanel(pdata)
            start += 7

    def parsepanel(self, data):
        if data is None:
            return None
        if len(data) != 7:
            print("Panel data length mismatch")
            return None
        key = struct.unpack('1B', data[0:1])[0]
        status = struct.unpack('1B', data[2:3])[0]
        switchon = (status & 0x01) > 0
        # tryheating = (status & 0x04) > 0
        temp = struct.unpack('1B', data[3:4])[0]
        tempset = struct.unpack('1B', data[4:5])[0]
        # notify = struct.unpack('1B', data[6:7])[0]

        self.set_accessory(key, "CurrentTemperature", temp)
        self.set_accessory(key, "TargetTemperature", tempset)
        self.set_accessory(key, "TargetHeatingCoolingState",
                           3 if switchon else 0)

    def on_message_from_get(self, mqttc, obj, msg):
        """
        处理来自TOPIC homebridge/from/get 的信息

        """
        # print(msg.topic + ' : ' + msg.payload)
        # message = json.loads(msg.payload)
        # print(json.dumps(message, indent=4, sort_keys=True))
        pass

    def on_message_from_set(self, mqttc, obj, msg):
        """
        处理来自TOPIC homebridge/from/set 的信息

        """
        # print(msg.topic + ' : ' + msg.payload)
        message = json.loads(msg.payload)
        if "name" in message and "characteristic" in message:
            # print(json.dumps(message, indent=4, sort_keys=True))
            switchon = 0
            tempset = 0
            addr = 0
            func = 0x01
            th_name = message["name"]
            th_characteristic = message["characteristic"]
            th_service_name = message["service_name"]
            th_value = message["value"]
            # print(th_name, th_characteristic, th_service_name, th_value)

            for k, v in self.thermostat_info.items():
                if th_name == k:
                    addr = v["addr"]
            if th_characteristic == "TargetHeatingCoolingState":
                # current I treat cooling as shutdown
                switchon = 0 if (th_value == 0) or (th_value == 2) else 1
                func = 0x02
                cmd = get_command(1, addr, switchon, func)
            elif th_characteristic == "TargetTemperature":
                tempset = th_value
                func = 0x04
                cmd = get_command(1, addr, tempset, func)
            # print(addr, switchon, tempset)
            print(fmt2hex(cmd))
        else:
            print("Unrecognized set:")
            print(json.dumps(message, indent=4, sort_keys=True))

    def on_message_from_response(self, mqttc, obj, msg):
        """
        处理来自TOPIC homebridge/from/response 的信息

        """
        # print(msg.topic + ' : ' + msg.payload)
        message = json.loads(msg.payload)
        if "ack" in message:
            # print("Response ack:")
            # print(json.dumps(message, indent=4, sort_keys=True))
            pass
        else:
            # print(json.dumps(message, indent=4, sort_keys=True))
            for ts in self.thermostat_names:
                if ts in message:
                    print(ts + " exists")
                else:
                    print("add " + ts + " to home")
                    self.add_accessory(ts)
            # time.sleep(1)
            # self.set_accessory_info()
            # self.set_accessory(1, "CurrentTemperature", 22)
        # self.message_callback_del("homebridge/from/response")

    def on_connect(self, mqttc, obj, flags, rc):
        print("Connected with result code " + str(rc))

        # Subscribing in on_connect() means that if we lose the connection and
        # reconnect then subscriptions will be renewed.
        # 订阅所有TOPIC
        self.subscribe("homebridge/#")
        # self.remove_accessories()
        self.get_accessories()

    def on_message(self, mqttc, obj, msg):
        # print(msg.topic + " " + str(msg.payload))
        pass

    def on_publish(self, mqttc, obj, mid):
        # print("mid: " + str(mid))
        pass

    def on_subscribe(self, mqttc, obj, mid, granted_qos):
        # print("Subscribed: " + str(mid) + " " + str(granted_qos))
        pass

    def on_log(self, mqttc, obj, level, string):
        # print("LOG: " + string)
        pass

    def run(self):
        self.message_callback_add(
            "homebridge/from/get", self.on_message_from_get)
        self.message_callback_add(
            "homebridge/from/set", self.on_message_from_set)
        self.message_callback_add(
            "homebridge/from/response", self.on_message_from_response)
        self.username_pw_set('rpi2-zerodayhong', 'rpi2rpi2')
        self.reconnect_delay_set()
        self.connect("10.0.0.5")
        # rc = 0
        # while rc == 0:
        #     rc = self.loop()
        # return rc
        self.loop_forever()


def get_command(addr, dev, val, func):
    # construct the bit-stream of an instruction
    if func == 0x01:
        PLUS = 0
    else:
        PLUS = 7 << 5
    cmd = struct.pack('6B', PLUS + addr, 0x06, dev, 0x04, func, val)
    _crc = crc.calc_string(cmd, crc.INITIAL_MODBUS)
    _crc = ((_crc & 0XFF) << 8) + ((_crc & 0xFF00) >> 8)
    return cmd + struct.pack('H', _crc)


def fmt2hex(str):
    if str is not None:
        return ':'.join(x.encode('hex') for x in str)  # python 2
        # return ':'.join(hex(x) for x in str) # python 3
    return None


if __name__ == '__main__':
    try:
        th = ThermostatMQTTClient()
        th.run()
    finally:
        th.disconnect()
