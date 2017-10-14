#! /usr/bin/python3
from gpiozero import LED
from time import sleep

blue = LED(17)
red = LED(27)
green = LED(22)
yellow = LED(23)

while True:
    for i in range(0,2):
        blue.on()
        red.on()
        green.on()
        yellow.on()
        sleep(0.5)
        blue.off()
        red.off()
        green.off()
        yellow.off()
        sleep(0.5)
    
    for i in range(0,10):
        for led in (blue, red, green, yellow):
            led.on()
            sleep(0.2)
            led.off()
        for led in (yellow, green, red, blue):
            led.on()
            sleep(0.2)
            led.off()

    sleep(2)
