#!/usr/bin/python/
# coding: utf-8
import time
import datetime
from luma.core.interface.serial import i2c, spi
from luma.core.render import canvas
from luma.oled.device import ssd1306, ssd1325, ssd1331, sh1106


def do_nothing(obj):
    pass


# rev.1 users set port=0
# substitute spi(device=0, port=0) below if using that interface
# serial = i2c(port=1, address=0x3C)
serial = spi(device=0, port=0)

# substitute ssd1331(...) or sh1106(...) below if using that device
# device = ssd1306(serial, rotate=1)
device = sh1106(serial)
# device.cleanup = do_nothing

print("Testing display Hello World")

with canvas(device) as draw:
    draw.rectangle(device.bounding_box, outline="white", fill="black")
    draw.text((30, 40), "Hello World", fill="white")

time.sleep(3)

print("Testing display ON/OFF...")
for _ in range(5):
    time.sleep(0.5)
    device.hide()

    time.sleep(0.5)
    device.show()

print("Testing clear display...")
time.sleep(2)
device.clear()

print("Testing screen updates...")
time.sleep(2)
for x in range(40):
    with canvas(device) as draw:
        now = datetime.datetime.now()
        draw.text((x, 4), str(now.date()), fill="white")
        draw.text((10, 16), str(now.time()), fill="white")
        time.sleep(0.1)

print("Quit, cleanup...")
