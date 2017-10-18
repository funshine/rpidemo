#!/usr/bin/python
# coding: utf-8
import struct
import crc
import threading
import time
import serial
import sys

# method to format hex


def fmt2hex(str):
    if str is not None:
        return ':'.join(x.encode('hex') for x in str)  # python 2
        # return ':'.join(hex(x) for x in str) # python 3
    return None

# method to genderate command


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


class Panel:
    def __init__(self, key, temp=20, tempset=5, switchon=True):
        self.key = key
        self.temp = temp
        self.tempset = tempset
        self.switchon = switchon
        self.tryheating = tempset > temp
        self.notify = False

    def __repr__(self):
        return '''Panel {0}:\n  Switch \t{1}\t\tHeating {4}\n  Temperature: \t{2}\t\tSet: \t{3}\n'''\
            .format(self.key, "on" if self.switchon else "off", self.temp, self.tempset, "yes" if self.tryheating else "no")

    def settemp(self, tempset):
        self.tempset = tempset
        self.tryheating = self.tempset > self.temp
        self.notify = True

    def sense(self, sense):
        self.temp = sense
        self.tryheating = self.tempset > self.temp

    def switch(self, on):
        self.switchon = True if on != 0 else False
        self.notify = True

    def getkey(self):
        return self.key

    def pack(self):
        key = struct.pack('B', self.key)
        stub1 = struct.pack('B', 7)
        status = struct.pack(
            'B', 0xf2 + ((0b1 if self.tryheating else 0b0) << 2) + (0b1 if self.switchon else 0b0))
        temp = struct.pack('2B', self.temp, self.tempset)
        stub2 = struct.pack('B', 0xff)
        notify = struct.pack('B', (0b1 if self.notify else 0b0))
        body = key + stub1 + status + temp + stub2 + notify
        if self.notify is True:
            self.notify = False
        return body


def testpanel():
    p1 = Panel(1)
    print(p1)
    print(fmt2hex(p1.pack()))
    print(p1.key, p1.temp, p1.tempset, p1.switchon, p1.tryheating)
    p1.switch(0)
    print("after switch off")
    print(p1)
    print(fmt2hex(p1.pack()))
    p1.switch(1)
    p1.settemp(17)
    print("after switch on, temp->17")
    print(p1)
    print(fmt2hex(p1.pack()))
    p1.sense(22)
    print("sense 22")
    print(p1)
    print(fmt2hex(p1.pack()))
    p1.sense(10)
    print("sense 10")
    print(p1)
    print(fmt2hex(p1.pack()))


class Device:
    def __init__(self, addr):
        self.panels = []
        self.addr = addr

    def __repr__(self):
        panelsinfo = ""
        for p in self.panels:
            panelsinfo += str(p)
        pnum = len(self.panels)
        if pnum > 2:
            return "Device {0} have ".format(self.addr) + str(len(self.panels)) + " Panels\n" + panelsinfo
        else:
            return "Device {0} has ".format(self.addr) + str(len(self.panels)) + " Panel\n" + panelsinfo

    def __check_crc(self, content, size):
        tmp = struct.unpack('2B', content[size:size + 2])
        return crc.calc_string(content[:size], crc.INITIAL_MODBUS) == ((tmp[0] << 8) + tmp[1])

    def __gen_header(self, addr, length):
        return struct.pack('8B', len(self.panels), ((length & 0xFF00) >> 8), length & 0xFF, 0x1f, addr, 0xff, 0xff, 0xff)

    def addpanel(self, panel):
        exist = False
        for p in self.panels:
            if p.getkey() == panel.getkey():
                exist = True
        if not exist:
            self.panels.append(panel)

    def process(self, cmd):
        if len(cmd) < 8:
            return None
        if not self.__check_crc(cmd, 6):
            return None
        addrplus = struct.unpack('B', cmd[0:1])[0]
        key = struct.unpack('B', cmd[2:3])[0]
        func = struct.unpack('B', cmd[4:5])[0]
        val = struct.unpack('B', cmd[5:6])[0]
        if func == 0x01:
            PLUS = 0
        else:
            PLUS = 7 << 5
        addr = addrplus - PLUS
        if addr != self.addr:
            return None

        h = ''
        pnum = len(self.panels)
        if pnum != 0:
            h = self.__gen_header(addr, 8 + 7 * pnum)
        else:
            h = self.__gen_header(addr, 8)

        body = ''
        for panel in self.panels:
            if panel.getkey() == key:
                # send cmd to the panel
                if func == 0x01:
                    # read info
                    pass
                elif func == 0x02:
                    # switch on/off
                    panel.switch(val)
                    print("Remote set:")
                    print(panel)
                elif func == 0x04:
                    # set temp
                    panel.settemp(val)
                    print("Remote set:")
                    print(panel)
                else:
                    pass
            body += panel.pack()

        _crc = crc.calc_string(h + body, crc.INITIAL_MODBUS)
        _crc = ((_crc & 0XFF) << 8) + ((_crc & 0xFF00) >> 8)

        return h + body + struct.pack('H', _crc)


def testdevice():
    d = Device(0)
    print(d)
    cmd = get_command(0, 1, 10, 2)
    print(fmt2hex(d.process(cmd)))
    d.addpanel(Panel(1))
    cmd = get_command(0, 1, 10, 2)
    print(fmt2hex(d.process(cmd)))
    d.addpanel(Panel(2))
    cmd = get_command(1, 1, 10, 2)
    print(fmt2hex(d.process(cmd)))
    d = Device(1)
    p = []
    print(d)
    cmd = get_command(1, 0, 0, 1)
    print(fmt2hex(d.process(cmd)))
    p.append(Panel(1))
    d.addpanel(p[0])
    cmd = get_command(1, 1, 10, 2)
    print(fmt2hex(d.process(cmd)))
    p.append(Panel(2))
    d.addpanel(p[1])
    cmd = get_command(1, 2, 10, 2)
    print(fmt2hex(d.process(cmd)))
    p.append(Panel(3))
    d.addpanel(p[2])
    cmd = get_command(2, 1, 10, 2)
    print(fmt2hex(d.process(cmd)))
    p.append(Panel(4))
    d.addpanel(p[3])
    p.append(Panel(5))
    d.addpanel(p[4])
    cmd = get_command(1, 0, 0, 1)
    print(fmt2hex(d.process(cmd)))
    cmd = get_command(1, 0, 0, 1)
    print(fmt2hex(d.process(cmd)))

    # 05:00:2b:1f:01:ff:ff:ff:01:07:f2:13:0c:ff:00:02:07:f2:15:07:ff:00:03:07:f3:14:06:ff:00:04:07:f3:15:08:ff:00:05:07:f3:14:0f:ff:00
    p[0].switch(0)
    p[0].sense(0x13)
    p[0].settemp(0x0c)
    p[1].switch(0)
    p[1].sense(0x15)
    p[1].settemp(0x07)
    p[2].switch(1)
    p[2].sense(0x14)
    p[2].settemp(0x06)
    p[3].switch(1)
    p[3].sense(0x15)
    p[3].settemp(0x08)
    p[4].switch(1)
    p[4].sense(0x14)
    p[4].settemp(0x0f)
    cmd = get_command(1, 0, 0, 1)
    print(fmt2hex(d.process(cmd)))
    cmd = get_command(1, 0, 0, 1)
    print(fmt2hex(d.process(cmd)))
    p[4].settemp(0x18)
    cmd = get_command(1, 0, 0, 1)
    print(fmt2hex(d.process(cmd)))


class InputThread(threading.Thread):
    def __init__(self, dev):
        threading.Thread.__init__(self)
        self.running = False
        self.sensemode = True
        self.device = dev

    def run(self):
        self.running = True
        func = 0x01
        val = 0
        while self.running:
            try:
                vals = raw_input(
                    'Enter key, value(temperature/on/off), seperate with space: ').split()
            except KeyboardInterrupt:
                print("User abort!")

            print(vals)
            if len(vals) == 1 and vals[0].upper() == 'S':
                self.sensemode = not self.sensemode
                print("Sense mode: ", self.sensemode)
                continue

            if len(vals) < 2:
                print("Must provide key and value")
                continue
            try:
                key = int(vals[0])
                print(key)
            except ValueError as ve:
                print('Key must be numbers')
                print(ve)
                continue

            if self.sensemode:
                try:
                    temp = int(vals[1])
                    func = 0x01
                    val = temp
                    print(temp)
                except ValueError as ve:
                    print('Values must be temperature')
                    print(ve)
                    continue
            else:
                if vals[1].upper() == 'ON':
                    func = 0x02
                    val = 1
                    print(vals[1])
                elif vals[1].upper() == 'OFF':
                    func = 0x02
                    val = 0
                    print(vals[1])
                else:
                    try:
                        temp = int(vals[1])
                        func = 0x04
                        val = temp
                        print(temp)
                    except ValueError as ve:
                        print('Values must be temperature or "on"/"off"')
                        print(ve)
                        continue

            for panel in self.device.panels:
                if panel.getkey() == key:
                    # send cmd to the panel
                    if func == 0x01:
                        # sense mode
                        panel.sense(val)
                        print("Local sense:")
                        print(panel)
                    if func == 0x02:
                        # switch on/off
                        panel.switch(val)
                        print("Local set:")
                        print(panel)
                    elif func == 0x04:
                        # set temp
                        panel.settemp(val)
                        print("Local set:")
                        print(panel)
                    else:
                        pass


class SerialThread(threading.Thread):
    def __init__(self, dev, port, timeout):
        threading.Thread.__init__(self)
        self.running = False
        self.device = dev
        self.port = port
        self.timeout = timeout
        self.serial = None

    def open(self):
        try:
            self.serial = serial.Serial(port=self.port, timeout=self.timeout)
            if self.serial.isOpen() == True:
                print("serial port is already open, close and reopen")
                self.serial.close()
            
            self.serial.open()
        except serial.SerialException as e:
            print("open function:")
            sys.stderr.write(str(e) + '\n')

    def close(self):
        if self.serial is None:
            return
        try:
            self.serial.close()
            print("close port success")
        except serial.SerialException as e:
            sys.stderr.write(str(e) + ' while closing serial port')

    def run(self):
        self.running = True
        try:
            self.open()
        except serial.SerialException as se:
            print("run function: ", se)
            self.running = False

        if self.serial is None:
            return

        while self.running:
            try:
                cmd = self.serial.read(8)
                print("Receive from serial: ", fmt2hex(cmd))
                result = self.device.process(cmd)
                if result is None:
                    continue
                print("Send to serial: ", fmt2hex(result))
                while result != '':
                    n = self.serial.write(result)
                    result = result[n:]

            except serial.SerialTimeoutException as toe:
                print(str(toe))
                self.running = False
            except serial.SerialException as se:
                print(str(se))
                self.running = False


def main():
    # testpanel()
    # testdevice()
    warmdev = Device(1)
    warmpanels = [Panel(1), Panel(2), Panel(3), Panel(4), Panel(5)]
    for p in warmpanels:
        warmdev.addpanel(p)

    try:
        cmdthread = InputThread(warmdev)
        serthread = SerialThread(warmdev, "/dev/tty.usbserial-FTVLKNBG", 10)
        cmdthread.start()
        print("InputThread started")
        serthread.start()
        print("SerialThread started")
        while 1:
            time.sleep(.1)
    except KeyboardInterrupt:
        print("attempting to close threads.")
        serthread.close()
        cmdthread.running = False
        serthread.running = False
        cmdthread.join()
        serthread.join()
        print("threads successfully closed")
    finally:
        serthread.close()


if __name__ == '__main__':
    main()
