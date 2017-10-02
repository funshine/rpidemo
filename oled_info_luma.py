#!/usr/bin/python/
# coding: utf-8
import os
import time
import socket
import fcntl
import struct
import requests
import platform
from luma.core.interface.serial import i2c, spi
from luma.core.render import canvas
from luma.oled.device import ssd1306, ssd1325, ssd1331, sh1106
from PIL import ImageFont

def raminfo():
    with open('/proc/meminfo') as f:
        total = float(f.readline().split()[1])
        free = float(f.readline().split()[1])
    return format((total-free)/total, '.1%')
def diskinfo():
    st = os.statvfs('/')
    total = float(st.f_blocks * st.f_frsize)
    used = float(st.f_blocks - st.f_bfree) * st.f_frsize
    return format(used/total, '.1%')
def cpuinfo():
    with open('/proc/stat') as f:
        info = f.readline().split()
        t0 = float(info[1]) + float(info[2]) + float(info[3])
        s0 = t0 + float(info[4]) + float(info[5]) + float(info[6]) + float(info[7])
    time.sleep(0.033)
    with open('/proc/stat') as f:
        info = f.readline().split()
        t1 = float(info[1]) + float(info[2]) + float(info[3])
        s1 = t1 + float(info[4]) + float(info[5]) + float(info[6]) + float(info[7])
    return format((t1-t0)/(s1-s0), '.1%')
def cputemp():
    with open('/sys/class/thermal/thermal_zone0/temp') as f:
        temp = float(f.readline())
    return format(temp/1000, '.1f')
def wifiinfo():
    with open('/proc/net/wireless') as f:
        f.readline()
        f.readline()
        info = f.readline().split()
    return info[3][:-1]
def get_ip_address(ifname):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(fcntl.ioctl(
        s.fileno(),
        0x8915,  # SIOCGIFADDR
        struct.pack('256s', ifname[:15])
    )[20:24])
def make_font(name, size):
    font_path = os.path.abspath(os.path.join(
        os.path.dirname(__file__), 'fonts', name))
    return ImageFont.truetype(font_path, size)
def do_nothing(obj):
    pass
IP = requests.get('http://ip.3322.net').text

# rev.1 users set port=0
# substitute spi(device=0, port=0) below if using that interface
# serial = i2c(port=1, address=0x3C)
serial = spi(device=0, port=0)

# substitute ssd1331(...) or sh1106(...) below if using that device
# device = ssd1306(serial, rotate=1)
device = sh1106(serial)
# device.cleanup = do_nothing

font = make_font("code2000.ttf", 12)
# font2 = make_font("tiny.ttf", 8)
font2 = ImageFont.load_default()
while True:
    with canvas(device) as draw:
        # Initialize background.
        draw.rectangle(device.bounding_box, outline=0, fill=0)
        padding = 1
        top = padding
        x = padding
        draw.text((x, top), time.strftime(" %Y-%m-%d %H:%M:%S ",time.localtime(time.time())), font=font, fill=255)
        draw.text((x, top+14), platform.system() + ' ' + platform.release(), font=font2, fill=255)
        draw.text((x, top+24), 'disk:' + diskinfo() + '  RAM:' + raminfo(), font=font2, fill=255)
        draw.text((x, top+34), 'temp:' + cputemp() + 'C  CPU:' + cpuinfo(), font=font2, fill=255)
        # draw.text((x, top+44), 'signal:' + '-60' + 'dBm', font=font2, fill=255)
        draw.text((x, top+44), 'LAN:' + get_ip_address('eth0'), font=font2, fill=255)
        draw.text((x, top+54), 'WAN:' + IP, font=font2, fill=255)
        time.sleep(1)
