#!/usr/bin/python/
# coding: utf-8
import os
import time
import socket
import fcntl
import struct
import requests
import Adafruit_GPIO.SPI as SPI
import Adafruit_SSD1306
import Image
import ImageDraw
import ImageFont
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
IP = requests.get('http://ip.3322.net').text
# Raspberry Pi pin configuration:
RST = 25
DC = 24
SPI_PORT = 0
SPI_DEVICE = 0
# 128x64 display with hardware SPI:
disp = Adafruit_SSD1306.SSD1306_128_64(rst=RST, dc=DC, spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE, max_speed_hz=8000000))
# Initialize library.
disp.begin()
# Clear display.
disp.clear()
while True:
    disp.display()
    # Create blank image for drawing.
    width = disp.width
    height = disp.height
    image = Image.new('1', (width, height))
    # Get drawing object to draw on image.
    draw = ImageDraw.Draw(image)
    # Initialize background.
    draw.rectangle((0,0,width,height), outline=0, fill=0)
    padding = 1
    top = padding
    x = padding
    font = ImageFont.load_default()
    draw.text((x, top), time.strftime(" %Y-%m-%d %H:%M:%S ",time.localtime(time.time())), font=font, fill=255)
    draw.text((x, top+14), 'disk:' + diskinfo() + '  RAM:' + raminfo(), font=font, fill=255)
    draw.text((x, top+24), 'temp:' + cputemp() + 'C  CPU:' + cpuinfo(), font=font, fill=255)
    draw.text((x, top+34), 'signal:' + '-60' + 'dBm', font=font, fill=255)
    draw.text((x, top+44), 'LAN:' + get_ip_address('eth0'), font=font, fill=255)
    draw.text((x, top+54), 'WAN:' + IP, font=font, fill=255)
    # Display image.
    disp.image(image)
    disp.display()