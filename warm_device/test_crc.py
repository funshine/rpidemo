#!/usr/bin/python
# coding: utf-8

import crc

def crc16(x, invert):
    a = 0xFFFF
    b = 0xA001
    for byte in x:
        a ^= ord(byte)
        for i in range(8):
            last = a % 2
            a >>= 1
            if last == 1:
                a ^= b
    s = hex(a).upper()
 
    return s[4:6]+s[2:4] if invert == True else s[2:4]+s[4:6]

def main():
    st = "a"
    print("crc16: ")
    print(crc16(st, False))
    print("warm crc: ")
    print(hex(crc.calc_string(st, crc.INITIAL_MODBUS)))

if __name__ == '__main__':
    main()