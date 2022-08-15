import math
import socket
import sys
import webbrowser
from enum import Enum
import time
from random import *
import threading

from vpython import vector

#from sandbox.audio_spectrum_analyzer.audio_spectrum import *
from sandbox.audio_spectrum_analyzer.Realtime_PyAudio_FFT_lib.run_FFT_analyzer import *

# CONFIG
MAX_PACKETS = 255

UDP_IP = "192.168.0.10"
UDP_PORT = 4210

TYPE_HEADER = 0xFE
TYPE_BODY = 0xBB
TYPE_SPECTRUM = 0xAB

TIME_FOR_1_ANIMATIONS_IN_MS = 5000

class Version(Enum):
    TEST = 0
    VERSION1 = 1
    VERSION1_1 = 2


class Type(Enum):
    FULL_FRAME = 0
    LEDS_TO_TURN_ON = 1
    WHOLE_ANIMATION = 2


CURRENT_VERSION = Version.TEST
TYPE = Type.FULL_FRAME


# # # # # # # # # # # # # # # # # # # # # # # # # # #


class LEDFrame:
    rgb = [0] * 768

    def __init__(self):
        self.rgb = [0] * 768

    def fill_all_red(self):
        self.rgb = [0xFF] * 256 + [0x0] * 512

    def fill_all_green(self):
        self.rgb = [0x0] * 256 + [0xFF] * 256 + [0x0] * 256

    def fill_all_blue(self):
        self.rgb = [0x0] * 512 + [0xFF] * 256

    def getTotalSize(self):
        return len(self.rgb)

    def clear(self):
        self.rgb = [0] * 768

    def drawColumn(self, x, y, level, r, g, b):
        for z in range(0, level + 1):
            self.turnOnLed(x, y, z, r, g, b)

    def getLedColor(self, x, y, z):
        r = 0
        g = 0
        b = 0

        if x < 0:
            return None
        if x > 7:
            return None
        if y < 0:
            return None
        if y > 7:
            return None
        if z < 0:
            return None
        if z > 7:
            return None
        if r < 0:
            return None
        if r > 15:
            return None
        if g < 0:
            return None
        if g > 15:
            return None
        if b < 0:
            return None
        if b > 15:
            return None

        index = int(((64 * z) + (y * 8) + x) / 8)
        position = ((64 * z) + (y * 8) + x) % 8


        r_bit1 = (self.rgb[index] & (1 << position)) >> position
        r_bit2 = (self.rgb[index + 64] & (1 << position)) >> position
        r_bit3 = (self.rgb[index + 128] & (1 << position)) >> position
        r_bit4 = (self.rgb[index + 192] & (1 << position)) >> position

        g_bit1 = (self.rgb[index + 256] & (1 << position)) >> position
        g_bit2 = (self.rgb[index + 64 + 256] & (1 << position)) >> position
        g_bit3 = (self.rgb[index + 128 + 256] & (1 << position)) >> position
        g_bit4 = (self.rgb[index + 192 + 256] & (1 << position)) >> position

        b_bit1 = (self.rgb[index + 512] & (1 << position)) >> position
        b_bit2 = (self.rgb[index + 64 + 512] & (1 << position)) >> position
        b_bit3 = (self.rgb[index + 128 + 512] & (1 << position)) >> position
        b_bit4 = (self.rgb[index + 192 + 512] & (1 << position)) >> position

        r = r_bit1 | (r_bit2 << 1) | (r_bit3 << 2) | (r_bit4 << 3)
        g = g_bit1 | (g_bit2 << 1) | (g_bit3 << 2) | (g_bit4 << 3)
        b = b_bit1 | (b_bit2 << 1) | (b_bit3 << 2) | (b_bit4 << 3)

        return r, g, b

    def turnOnLed(self, x, y, z, r, g, b):
        if x < 0:
            x = 0
        if x > 7:
            x = 7
        if y < 0:
            y = 0
        if y > 7:
            y = 7
        if z < 0:
            z = 0
        if z > 7:
            z = 7
        if r < 0:
            r = 0
        if r > 15:
            r = 15
        if g < 0:
            g = 0
        if g > 15:
            g = 15
        if b < 0:
            b = 0
        if b > 15:
            b = 15

        index = int(((64 * z) + (y * 8) + x) / 8)
        position = ((64 * z) + (y * 8) + x) % 8

        # red
        if (r & 0b0001) > 0:
            self.rgb[index] = self.rgb[index] | (1 << position)
        else:
            self.rgb[index] = self.rgb[index] & ~(1 << position)

        if ((r & 0b0010) >> 1) > 0:
            self.rgb[index + 64] = self.rgb[index + 64] | (1 << position)
        else:
            self.rgb[index + 64] = self.rgb[index + 64] & ~(1 << position)

        if ((r & 0b0100) >> 2) > 0:
            self.rgb[index + 128] = self.rgb[index + 128] | (1 << position)
        else:
            self.rgb[index + 128] = self.rgb[index + 128] & ~(1 << position)

        if ((r & 0b1000) >> 3) > 0:
            self.rgb[index + 192] = self.rgb[index + 192] | (1 << position)
        else:
            self.rgb[index + 192] = self.rgb[index + 192] & ~(1 << position)

        # green
        if (g & 0b0001) > 0:
            self.rgb[index + 256] = self.rgb[index + 256] | (1 << position)
        else:
            self.rgb[index + 256] = self.rgb[index + 256] & ~(1 << position)

        if ((g & 0b0010) >> 1) > 0:
            self.rgb[index + 64 + 256] = self.rgb[index + 64 + 256] | (1 << position)
        else:
            self.rgb[index + 64 + 256] = self.rgb[index + 64 + 256] & ~(1 << position)

        if ((g & 0b0100) >> 2) > 0:
            self.rgb[index + 128 + 256] = self.rgb[index + 128 + 256] | (1 << position)
        else:
            self.rgb[index + 128 + 256] = self.rgb[index + 128 + 256] & ~(1 << position)

        if ((g & 0b1000) >> 3) > 0:
            self.rgb[index + 192 + 256] = self.rgb[index + 192 + 256] | (1 << position)
        else:
            self.rgb[index + 192 + 256] = self.rgb[index + 192 + 256] & ~(1 << position)

        # blue
        if (b & 0b0001) > 0:
            self.rgb[index + 512] = self.rgb[index + 512] | (1 << position)
        else:
            self.rgb[index + 512] = self.rgb[index + 512] & ~(1 << position)

        if ((b & 0b0010) >> 1) > 0:
            self.rgb[index + 64 + 512] = self.rgb[index + 64 + 512] | (1 << position)
        else:
            self.rgb[index + 64 + 512] = self.rgb[index + 64 + 512] & ~(1 << position)

        if ((b & 0b0100) >> 2) > 0:
            self.rgb[index + 128 + 512] = self.rgb[index + 128 + 512] | (1 << position)
        else:
            self.rgb[index + 128 + 512] = self.rgb[index + 128 + 512] & ~(1 << position)

        if ((b & 0b1000) >> 3) > 0:
            self.rgb[index + 192 + 512] = self.rgb[index + 192 + 512] | (1 << position)
        else:
            self.rgb[index + 192 + 512] = self.rgb[index + 192 + 512] & ~(1 << position)


    def getData(self, starting_index, length):
        return bytes(self.rgb[starting_index:starting_index + length])

    def updateColumn(self, level, xCord, yCord):
        """ view from top of the matrix. Each 2x2 matrix will map one sound frequency range
                            00 01
                            10 11
           00  10     20  30     40  50     60   70
           01  11     21  31     41  51     61   71
           02  12     22  32     42  52     62   72
           03  13     23  33     43  53     63   73
           04  14     24  34     44  54     64   74
           05  15     25  35     45  55     65   75
           06  16     26  36     46  56     66   76
           07  17     27  37     47  57     67   77
           """
        coordinates = [[xCord * 2, yCord * 2], [xCord * 2 + 1, yCord * 2],
                       [xCord * 2, yCord * 2 + 1], [xCord * 2 + 1, yCord * 2 + 1]]

        for pair in coordinates:
            for zCord in range(0, level):
                if zCord == 7:
                    self.turnOnLed(pair[0], pair[1], zCord, 15, 0, 15)
                elif zCord >= 5:
                    self.turnOnLed(pair[0], pair[1], zCord, 15, 0, 0)
                elif zCord >= 3:
                    self.turnOnLed(pair[0], pair[1], zCord, 15, 15, 0)
                else:
                    self.turnOnLed(pair[0], pair[1], zCord, 0, 15, 0)


class LEDHeader:
    packet_type = bytes([TYPE_HEADER])
    version = 0
    type = 0
    body_size = 0

    def __init__(self, frame_to_send):
        self.type = bytes([Type.FULL_FRAME.value])
        self.version = bytes([Version.VERSION1.value])
        total_size = frame_to_send.getTotalSize()
        self.body_size = bytes([(total_size & 0xFF00) >> 8, total_size & 0xFF])

    def constructPacket(self):
        packet = self.packet_type + self.version + self.type + self.body_size
        #print(f'Packet: {packet}')
        return packet


class LEDBody:
    message = bytes([TYPE_BODY])

    def __init__(self, packet_to_send):
        self.message = self.message + packet_to_send

    def constructPacket(self):
        return self.message


def sendHeader(frame_to_send):
    header = LEDHeader(frame_to_send)
    MESSAGE = header.constructPacket()

    #print(MESSAGE)

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # UDP

    sock.sendto(MESSAGE, (UDP_IP, UDP_PORT))


def sendBody(packet_to_send):
    body = LEDBody(packet_to_send)

    MESSAGE = body.constructPacket()
    #print(MESSAGE)

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # UDP

    sock.sendto(MESSAGE, (UDP_IP, UDP_PORT))


def sendBodies(frame_to_send):
    bytes_sent = 0
    bytes_to_send = frame_to_send.getTotalSize()

    while bytes_to_send > 0:
        if bytes_to_send > (MAX_PACKETS - 1):
            packet = frame_to_send.getData(bytes_sent, MAX_PACKETS - 1)
            bytes_sent += MAX_PACKETS - 1
            bytes_to_send -= MAX_PACKETS - 1
        else:
            packet = frame_to_send.getData(bytes_sent, bytes_to_send)
            bytes_sent += bytes_to_send
            bytes_to_send = 0

        sendBody(packet)


def sendFrame(obj, frame_to_send):
    sendHeader(frame_to_send)
    sendBodies(frame_to_send)

    obj.cube.update_simulated_cube(frame_to_send)

    # send header
    # send bodies


def sendSpectrum(obj, barsData):
    data = [0] * (1 + 32)
    data[0] = TYPE_SPECTRUM

    dataIndex = 1
    for i in range(0, 63, 2):
        test1 = barsData[i + 1] & 0b1111
        test2 = barsData[i] & 0b00001111

        # if test1 < 1 or test1 > 7:
        # print("[ERROR] Wrong bar level")

        # if test2 < 1 or test2 > 7:
        # print("[ERROR] Wrong bar level")

        data[dataIndex] = ((barsData[i + 1] & 0b1111) << 4) | (barsData[i] & 0b00001111)
        dataIndex += 1

    MESSAGE = bytes(data)

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # UDP
    sock.sendto(MESSAGE, (UDP_IP, UDP_PORT))

    frame = LEDFrame()
    #print(barsData)

    for i, bar in enumerate(barsData):
        x = int(i / 8)
        y = i % 8

        r, g, b = 0, 0, 0

        if x == 0:
            r = 1
            g = 1
            b = 8
        elif x == 1:
            r = 5
            g = 1
            b = 10
        elif x == 2:
            r = 8
            g = 1
            b = 17
        elif x == 3:
            r = 11
            g = 3
            b = 9
        elif x == 4:
            r = 13
            g = 5
            b = 7
        elif x == 5:
            r = 14
            g = 7
            b = 6
        elif x == 6:
            r = 15
            g = 9
            b = 4
        elif x == 7:
            r = 14
            g = 15
            b = 3

        frame.drawColumn(x, y, bar, r, g, b)

    obj.cube.update_simulated_cube(frame)


def current_milli_time():
    return round(time.time() * 1000)


class DoColorWheelAnimation(threading.Thread):
    def __init__(self, obj, *args, **kwargs):
        super(DoColorWheelAnimation, self).__init__(*args, **kwargs)
        self.obj = obj

    def run(self):
        color_wheel(self.obj)


def color_wheel(obj):
    frame = LEDFrame()
    rr = 1
    gg = 1
    bb = 1
    ranx = 0
    rany = 0
    swiper = 0
    xx = 0
    yy = 0
    zz = 0
    ww = 0

    start = current_milli_time()

    while current_milli_time() - start < TIME_FOR_1_ANIMATIONS_IN_MS:
        if obj.cube.abort_animation_thread:
            return

        swiper = randint(0, 3)
        ranx = randint(0, 16)
        rany = randint(0, 16)

        for xx in range(0, 8):
            for yy in range(0, 8):
                for zz in range(0, 8):
                    frame.turnOnLed(xx, yy, zz, ranx, 0, rany)
            sendFrame(obj, frame)
            time.sleep(0.050)

        ranx = randint(0, 16)
        rany = randint(0, 16)

        for xx in reversed(range(0, 8)) :
            for yy in range(0, 8):
                for zz in range(0, 8):
                    frame.turnOnLed(xx, yy, zz, ranx, rany, 0)
            sendFrame(obj, frame)
            time.sleep(0.050)

        ranx = randint(0, 16)
        rany = randint(0, 16)

        for xx in range(0, 8):
            for yy in range(0, 8):
                for zz in range(0, 8):
                    frame.turnOnLed(xx, yy, zz, 0, ranx, rany)
            sendFrame(obj, frame)
            time.sleep(0.050)

        ranx = randint(0, 16)
        rany = randint(0, 16)
        for xx in reversed(range(0, 8)) :
            for yy in range(0, 8):
                for zz in range(0, 8):
                    frame.turnOnLed(xx, yy, zz, ranx, rany, 0)
            sendFrame(obj, frame)
            time.sleep(0.050)


def brightness_3_colors():
    frame = LEDFrame()

    delay = (TIME_FOR_1_ANIMATIONS_IN_MS / 3) / 16

    for brightness in range(0, 16):
        for z in range(0, 8):
            for y in range(0, 8):
                for x in range(0, 8):
                    frame.turnOnLed(x, y, z, brightness, 0, 0)
        sendFrame(frame)
        time.sleep(delay)

    for brightness in range(0, 16):
        for z in range(0, 8):
            for y in range(0, 8):
                for x in range(0, 8):
                    frame.turnOnLed(x, y, z, 0, brightness, 0)
        sendFrame(frame)
        time.sleep(delay)

    for brightness in range(0, 16):
        for z in range(0, 8):
            for y in range(0, 8):
                for x in range(0, 8):
                    frame.turnOnLed(x, y, z, 0, 0, brightness)
        sendFrame(frame)
        time.sleep(delay)


class DoSinWaveAnimation(threading.Thread):
    def __init__(self, obj, *args, **kwargs):
        super(DoSinWaveAnimation, self).__init__(*args, **kwargs)
        self.obj = obj

    def run(self):
        sinwaveTwo(self.obj)


def sinwaveTwo(obj):
    sinewavearray = [0] * 8
    addr = 0
    sinemult = [0] * 8
    colselect = 0
    rr = 0
    gg = 0
    bb = 15
    addrt = 0

    sinewavearrayOLD = [0] * 8
    select = 0
    subZ = -7
    subT = 7
    multi = 0
    sinewavearray[0] = 0
    sinemult[0] = 1
    sinewavearray[1] = 1
    sinemult[1] = 1
    sinewavearray[2] = 2
    sinemult[2] = 1
    sinewavearray[3] = 3
    sinemult[3] = 1
    sinewavearray[4] = 4
    sinemult[4] = 1
    sinewavearray[5] = 5
    sinemult[5] = 1
    sinewavearray[6] = 6
    sinemult[6] = 1
    sinewavearray[7] = 7
    sinemult[7] = 1

    frame = LEDFrame()

    start = current_milli_time()

    while (current_milli_time() - start) < TIME_FOR_1_ANIMATIONS_IN_MS:
        if obj.cube.abort_animation_thread:
            return

        for addr in range(0, 8):
            if sinewavearray[addr] == 7:
                sinemult[addr] = -1
            if sinewavearray[addr] == 0:
                sinemult[addr] = 1
            sinewavearray[addr] = sinewavearray[addr] + sinemult[addr]

        if sinewavearray[0] == 7:
            select = randint(0, 3)
            if select == 0:
                rr = randint(1, 16)
                gg = randint(1, 16)
                bb = 0

            if select == 1:
                rr = randint(1, 16)
                gg = 0
                bb = randint(1, 16)

            if select == 2:
                rr = 0
                gg = randint(1, 16)
                bb = randint(1, 16)

        for addr in range(0, 8):
            frame.turnOnLed(sinewavearrayOLD[addr], addr, 0, 0, 0, 0)
            frame.turnOnLed(sinewavearrayOLD[addr], 0, addr, 0, 0, 0)
            frame.turnOnLed(sinewavearrayOLD[addr], subT - addr, 7, 0, 0, 0)
            frame.turnOnLed(sinewavearrayOLD[addr], 7, subT - addr, 0, 0, 0)
            frame.turnOnLed(sinewavearray[addr], addr, 0, rr, gg, bb)
            frame.turnOnLed(sinewavearray[addr], 0, addr, rr, gg, bb)
            frame.turnOnLed(sinewavearray[addr], subT - addr, 7, rr, gg, bb)
            frame.turnOnLed(sinewavearray[addr], 7, subT - addr, rr, gg, bb)

        for addr in range(1, 7):
            frame.turnOnLed(sinewavearrayOLD[addr + multi * 1], addr, 1, 0, 0, 0)
            frame.turnOnLed(sinewavearrayOLD[addr + multi * 1], 1, addr, 0, 0, 0)
            frame.turnOnLed(sinewavearrayOLD[addr + multi * 1], subT - addr, 6, 0, 0, 0)
            frame.turnOnLed(sinewavearrayOLD[addr + multi * 1], 6, subT - addr, 0, 0, 0)
            frame.turnOnLed(sinewavearray[addr + multi * 1], addr, 1, rr, gg, bb)
            frame.turnOnLed(sinewavearray[addr + multi * 1], 1, addr, rr, gg, bb)
            frame.turnOnLed(sinewavearray[addr + multi * 1], subT - addr, 6, rr, gg, bb)
            frame.turnOnLed(sinewavearray[addr + multi * 1], 6, subT - addr, rr, gg, bb)

        for addr in range(2, 6):
            frame.turnOnLed(sinewavearrayOLD[addr + multi * 2], addr, 2, 0, 0, 0)
            frame.turnOnLed(sinewavearrayOLD[addr + multi * 2], 2, addr, 0, 0, 0)
            frame.turnOnLed(sinewavearrayOLD[addr + multi * 2], subT - addr, 5, 0, 0, 0)
            frame.turnOnLed(sinewavearrayOLD[addr + multi * 2], 5, subT - addr, 0, 0, 0)
            frame.turnOnLed(sinewavearray[addr + multi * 2], addr, 2, rr, gg, bb)
            frame.turnOnLed(sinewavearray[addr + multi * 2], 2, addr, rr, gg, bb)
            frame.turnOnLed(sinewavearray[addr + multi * 2], subT - addr, 5, rr, gg, bb)
            frame.turnOnLed(sinewavearray[addr + multi * 2], 5, subT - addr, rr, gg, bb)

        for addr in range(3, 6):
            frame.turnOnLed(sinewavearrayOLD[addr + multi * 3], addr, 3, 0, 0, 0)
            frame.turnOnLed(sinewavearrayOLD[addr + multi * 3], 3, addr, 0, 0, 0)
            frame.turnOnLed(sinewavearrayOLD[addr + multi * 3], subT - addr, 4, 0, 0, 0)
            frame.turnOnLed(sinewavearrayOLD[addr + multi * 3], 4, subT - addr, 0, 0, 0)
            frame.turnOnLed(sinewavearray[addr + multi * 3], addr, 3, rr, gg, bb)
            frame.turnOnLed(sinewavearray[addr + multi * 3], 3, addr, rr, gg, bb)
            frame.turnOnLed(sinewavearray[addr + multi * 3], subT - addr, 4, rr, gg, bb)
            frame.turnOnLed(sinewavearray[addr + multi * 3], 4, subT - addr, rr, gg, bb)

        for addr in range(0,8):
            sinewavearrayOLD[addr] = sinewavearray[addr]

        sendFrame(obj, frame)
        time.sleep(0.050)
        frame.clear()


class DoRainAnimation(threading.Thread):
    def __init__(self, obj, *args, **kwargs):
        super(DoRainAnimation, self).__init__(*args, **kwargs)
        self.obj = obj

    def run(self):
        rainVersionTwo(self.obj)


def rainVersionTwo(obj):
    x = [0] * 64
    y = [0] * 64
    z = [0] * 64
    addr = 0
    leds = 64
    bright = 1
    ledcolor = 0
    colowheel = 0

    xx = [0] * 64
    yy = [0] * 64
    zz = [0] * 64
    xold = [0] * 64
    yold = [0] * 64
    zold = [0] * 64
    slowdown = 0

    for addr in range(0, 64):
        x[addr] = randint(0, 7)
        y[addr] = randint(0, 7)
        z[addr] = randint(0, 7)
        xx[addr] = randint(0, 15)
        yy[addr] = randint(0, 15)
        zz[addr] = randint(0, 15)

    start = current_milli_time()

    frame = LEDFrame()

    while (current_milli_time() - start) < TIME_FOR_1_ANIMATIONS_IN_MS:
        if obj.cube.abort_animation_thread:
            return

        if ledcolor < 200:
            for addr in range(0, leds):
                frame.turnOnLed(xold[addr], yold[addr], zold[addr], 0, 0, 0)
            if z[addr] >= 7:
                frame.turnOnLed(x[addr], y[addr], z[addr], 0, 5, 15)
            if z[addr] == 6:
                frame.turnOnLed(x[addr], y[addr], z[addr], 0, 1, 9)
            if z[addr] == 5:
                frame.turnOnLed(x[addr], y[addr], z[addr], 0, 0, 10)
            if z[addr] == 4:
                frame.turnOnLed(x[addr], y[addr], z[addr], 1, 0, 11)
            if z[addr] == 3:
                frame.turnOnLed(x[addr], y[addr], z[addr], 3, 0, 12)
            if z[addr] == 2:
                frame.turnOnLed(x[addr], y[addr], z[addr], 10, 0, 15)
            if z[addr] == 1:
                frame.turnOnLed(x[addr], y[addr], z[addr], 10, 0, 10)
            if z[addr] <= 0:
                frame.turnOnLed(x[addr], y[addr], z[addr], 10, 0, 1)

        if 200 <= ledcolor < 300:
            for addr in range(0, leds):
                frame.turnOnLed(xold[addr], yold[addr], zold[addr], 0, 0, 0)
            if z[addr] >= 7:
                frame.turnOnLed(x[addr], y[addr], z[addr], 15, 15, 0)
            if z[addr] == 6:
                frame.turnOnLed(x[addr], y[addr], z[addr], 10, 10, 0)
            if z[addr] == 5:
                frame.turnOnLed(x[addr], y[addr], z[addr], 15, 5, 0)
            if z[addr] == 4:
                frame.turnOnLed(x[addr], y[addr], z[addr], 15, 2, 0)
            if z[addr] == 3:
                frame.turnOnLed(x[addr], y[addr], z[addr], 15, 1, 0)
            if z[addr] == 2:
                frame.turnOnLed(x[addr], y[addr], z[addr], 15, 0, 0)
            if z[addr] == 1:
                frame.turnOnLed(x[addr], y[addr], z[addr], 12, 0, 0)
            if z[addr] <= 0:
                frame.turnOnLed(x[addr], y[addr], z[addr], 10, 0, 0)

        ledcolor += 1

        if ledcolor >= 300:
            ledcolor = 0

        for addr in range(0, leds):
            xold[addr] = x[addr]
            yold[addr] = y[addr]
            zold[addr] = z[addr]

        sendFrame(obj, frame)
        time.sleep(0.04)

        for addr in range(0, leds):
            z[addr] = z[addr] - 1

            if z[addr] < randint(-100, 0):
                x[addr] = randint(0, 7)
                y[addr] = randint(0, 7)
                select = randint(0, 2)
                if select == 0:
                    xx[addr] = 0
                    zz[addr] = randint(0, 15)
                    yy[addr] = randint(0, 15)

                if select == 1:
                    xx[addr] = randint(0, 15)
                    zz[addr] = 0
                    yy[addr] = randint(0, 15)

                if select == 2:
                    xx[addr] = randint(0, 15)
                    zz[addr] = randint(0, 15)
                    yy[addr] = 0

                z[addr] = 7


def start_spectrum(duration):
    visualiser = SpectrumVisualizer()
    visualiser.startVisualisation(duration)


class DoFolderAnimation(threading.Thread):
    def __init__(self, obj, *args, **kwargs):
        super(DoFolderAnimation, self).__init__(*args, **kwargs)
        self.obj = obj

    def run(self):
        folder(self.obj)


def folder(obj):
    xx = 0
    yy = 0
    zz = 0
    pullback = [0] * 16
    state = 0
    backorfront = 0

    folderaddr = [0] * 16
    LED_Old = [0] * 16
    oldpullback = [0] * 16
    ranx = randint(0, 15)
    rany = randint(0, 15)
    ranz = randint(0, 15)
    ranselect = 0
    bot = 0
    top = 1
    right = 0
    left = 0
    back = 0
    front = 0
    side = 0
    side_select = 0

    folderaddr[0] = -7
    folderaddr[1] = -6
    folderaddr[2] = -5
    folderaddr[3] = -4
    folderaddr[4] = -3
    folderaddr[5] = -2
    folderaddr[6] = -1
    folderaddr[7] = 0

    for xx in range(0, 8):
        oldpullback[xx] = 0
        pullback[xx] = 0

    DELAY_5MS = 0.005 * 10
    DELAY_10MS = 0.010 * 10

    frame = LEDFrame()

    start = current_milli_time()
    while (current_milli_time() - start) < TIME_FOR_1_ANIMATIONS_IN_MS:
        if obj.cube.abort_animation_thread:
            return

        if top == 1:
            if side == 0:
                # top to left-side
                for yy in range(0, 8):
                    for xx in range (0, 8):
                        frame.turnOnLed(7 - LED_Old[yy], yy - oldpullback[yy], xx, 0, 0, 0)
                        frame.turnOnLed(7 - folderaddr[yy], yy - pullback[yy], xx, ranx, rany, ranz)

            if side == 2:
                # top to back-side
                for yy in range(0, 8):
                    for xx in range(0, 8):
                        frame.turnOnLed(7 - LED_Old[yy], xx, yy - oldpullback[yy], 0, 0, 0)
                        frame.turnOnLed(7 - folderaddr[yy], xx, yy - pullback[yy], ranx, rany, ranz)

            if side == 3:
                # top-side to front-side
                for yy in range(0, 8):
                    for xx in range(0, 8):
                        frame.turnOnLed(7 - LED_Old[7 - yy], xx, yy + oldpullback[yy], 0, 0, 0)
                        frame.turnOnLed(7 - folderaddr[7 - yy], xx, yy + pullback[yy], ranx, rany, ranz)

            if side == 1:
                # top-side to right
                for yy in range(0, 8):
                    for xx in range(0, 8):
                        frame.turnOnLed(7 - LED_Old[7 - yy], yy + oldpullback[yy], xx, 0, 0, 0)
                        frame.turnOnLed(7 - folderaddr[7 - yy], yy + pullback[yy], xx, ranx, rany, ranz)

        if right == 1:
            if side == 4:
                # right-side to top
                for yy in range(0, 8):
                    for xx in range(0, 8):
                        frame.turnOnLed(yy + oldpullback[7 - yy], 7 - LED_Old[7 - yy], xx, 0, 0, 0)
                        frame.turnOnLed(yy + pullback[7 - yy], 7 - folderaddr[7 - yy], xx, ranx, rany, ranz)

            if side == 3:
                # right-side to front-side
                for yy in range(0, 8):
                    for xx in range(0, 8):
                        frame.turnOnLed(xx, 7 - LED_Old[7 - yy], yy + oldpullback[yy], 0, 0, 0)
                        frame.turnOnLed(xx, 7 - folderaddr[7 - yy], yy + pullback[yy], ranx, rany, ranz)

            if side == 2:
                # right-side to back-side
                for yy in range(0, 8):
                    for xx in range(0, 8):
                        frame.turnOnLed(xx, 7 - LED_Old[yy], yy - oldpullback[yy], 0, 0, 0)
                        frame.turnOnLed(xx, 7 - folderaddr[yy], yy - pullback[yy], ranx, rany, ranz)

            if side == 5:
                # right-side to bottom
                for yy in range(0, 8):
                    for xx in range(0, 8):
                        frame.turnOnLed(yy - oldpullback[yy], 7 - LED_Old[yy], xx, 0, 0, 0)
                        frame.turnOnLed(yy - pullback[yy], 7 - folderaddr[yy], xx, ranx, rany, ranz)

        if left == 1:
            if side == 4:
                # left-side to top
                for yy in range(0, 8):
                    for xx in range(0, 8):
                        frame.turnOnLed(yy + oldpullback[yy], LED_Old[7 - yy], xx, 0, 0, 0)
                        frame.turnOnLed(yy + pullback[yy], folderaddr[7 - yy], xx, ranx, rany, ranz)

            if side == 3:
                # left-side to front-side
                for yy in range(0, 8):
                    for xx in range(0, 8):
                        frame.turnOnLed(xx, LED_Old[7 - yy], yy + oldpullback[yy], 0, 0, 0)
                        frame.turnOnLed(xx, folderaddr[7 - yy], yy + pullback[yy], ranx, rany, ranz)

            if side == 2:
            # left-side to back-side
                for yy in range(0, 8):
                    for xx in range(0, 8):
                        frame.turnOnLed(xx, LED_Old[yy], yy - oldpullback[yy], 0, 0, 0)
                        frame.turnOnLed(xx, folderaddr[yy], yy - pullback[yy], ranx, rany, ranz)

            if side == 5:
                # left-side to bottom
                for yy in range(0, 8):
                    for xx in range(0, 8):
                        frame.turnOnLed(yy - oldpullback[yy], LED_Old[yy], xx, 0, 0, 0)
                        frame.turnOnLed(yy - pullback[yy], folderaddr[yy], xx, ranx, rany, ranz)

        if back == 1:
            if side == 1:
                # back-side to right-side
                for yy in range(0, 8):
                    for xx in range(0, 8):
                        frame.turnOnLed(xx, yy + oldpullback[yy], LED_Old[7 - yy], 0, 0, 0)
                        frame.turnOnLed(xx, yy + pullback[yy], folderaddr[7 - yy], ranx, rany, ranz)

            if side == 4:
                # back-side to top-side
                for yy in range(0, 8):
                    for xx in range(0, 8):
                        frame.turnOnLed(yy + oldpullback[yy], xx, LED_Old[7 - yy], 0, 0, 0)
                        frame.turnOnLed(yy + pullback[yy], xx, folderaddr[7 - yy], ranx, rany, ranz)

            if side == 5:
                # back-side to bottom
                for yy in range(0, 8):
                    for xx in range(0, 8):
                        frame.turnOnLed(yy - oldpullback[yy], xx, LED_Old[yy], 0, 0, 0)
                        frame.turnOnLed(yy - pullback[yy], xx, folderaddr[yy], ranx, rany, ranz)

            if side == 0:
                # back-side to left-side
                for yy in range(0, 8):
                    for xx in range(0, 8):
                        frame.turnOnLed(xx, yy - oldpullback[yy], LED_Old[yy], 0, 0, 0)
                        frame.turnOnLed(xx, yy - pullback[yy], folderaddr[yy], ranx, rany, ranz)

        if bot == 1:
            if side == 1:
                # bottom-side to right-side
                for yy in range(0, 8):
                    for xx in range(0, 8):
                        frame.turnOnLed(LED_Old[7 - yy], yy + oldpullback[yy], xx, 0, 0, 0)
                        frame.turnOnLed(folderaddr[7 - yy], yy + pullback[yy], xx, ranx, rany, ranz)

            if side == 3:
                # bottom to front-side
                for yy in range(0, 8):
                    for xx in range(0, 8):
                        frame.turnOnLed(LED_Old[7 - yy], xx, yy + oldpullback[yy], 0, 0, 0)
                        frame.turnOnLed(folderaddr[7 - yy], xx, yy + pullback[yy], ranx, rany, ranz)

            if side == 2:
                # bottom to back-side
                for yy in range(0, 8):
                    for xx in range(0, 8):
                        frame.turnOnLed(LED_Old[yy], xx, yy - oldpullback[yy], 0, 0, 0)
                        frame.turnOnLed(folderaddr[yy], xx, yy - pullback[yy], ranx, rany, ranz)

            if side == 0:
                # bottom to left-side
                for yy in range(0, 8):
                    for xx in range(0, 8):
                        frame.turnOnLed(LED_Old[yy], yy - oldpullback[yy], xx, 0, 0, 0)
                        frame.turnOnLed(folderaddr[yy], yy - pullback[yy], xx, ranx, rany, ranz)

        if front == 1:
            if side == 0:
                # front-side to left-side
                for yy in range(0, 8):
                    for xx in range(0, 8):
                        frame.turnOnLed(xx, yy - oldpullback[yy], 7 - LED_Old[yy], 0, 0, 0)
                        frame.turnOnLed(xx, yy - pullback[yy], 7 - folderaddr[yy], ranx, rany, ranz)

            if side == 5:
                # front-side to bottom
                for yy in range(0, 8):
                    for xx in range(0, 8):
                        frame.turnOnLed(yy - oldpullback[yy], xx, 7 - LED_Old[yy], 0, 0, 0)
                        frame.turnOnLed(yy - pullback[yy], xx, 7 - folderaddr[yy], ranx, rany, ranz)

            if side == 4:
                # front-side to top-side
                for yy in range(0, 8):
                    for xx in range(0, 8):
                        frame.turnOnLed(yy + oldpullback[yy], xx, 7 - LED_Old[7 - yy], 0, 0, 0)
                        frame.turnOnLed(yy + pullback[yy], xx, 7 - folderaddr[7 - yy], ranx, rany, ranz)

            if side == 1:
                # front-side to right-side
                for yy in range(0, 8):
                    for xx in range(0, 8):
                        frame.turnOnLed(xx, yy + oldpullback[yy], 7 - LED_Old[7 - yy], 0, 0, 0)
                        frame.turnOnLed(xx, yy + pullback[yy], 7 - folderaddr[7 - yy], ranx, rany, ranz)

        sendFrame(obj, frame)
        time.sleep(DELAY_5MS)

        for xx in range(0, 8):
            LED_Old[xx] = folderaddr[xx]
            oldpullback[xx] = pullback[xx]

        if folderaddr[7] == 7:
            for zz in range(0, 8):
                pullback[zz] = pullback[zz] + 1

            if pullback[7] == 8: # finished with fold
                sendFrame(obj, frame)
                time.sleep(DELAY_10MS)

                ranselect = randint(0, 2)

                if ranselect == 0:
                    ranx = 0
                    rany = randint(1, 15)
                    ranz = randint(1, 15)

                if ranselect == 1:
                    ranx = randint(1, 15)
                    rany = 0
                    ranz = randint(1, 15)

                if ranselect == 2:
                    ranx = randint(1, 15)
                    rany = randint(1, 15)
                    ranz = 0

                side_select = randint(0, 2)

                if top == 1: # TOP
                    top = 0
                    if side == 0: # top to left
                        left = 1
                        if side_select == 0:
                            side = 2
                        if side_select == 1:
                            side = 3
                        if side_select == 2:
                            side = 5
                    elif side == 1: # top to right
                        right = 1
                        if side_select == 0:
                            side = 5
                        if side_select == 1:
                            side = 2
                        if side_select == 2:
                            side = 3
                    elif side == 2: # top to back
                        back = 1
                        if side_select == 0:
                            side = 0
                        if side_select == 1:
                            side = 1
                        if side_select == 2:
                            side = 5
                    elif side == 3: # top to front
                        front = 1
                        if side_select == 0:
                            side = 0
                        if side_select == 1:
                            side = 1
                        if side_select == 2:
                            side = 5
                elif bot == 1: # BOTTOM
                    bot = 0
                    if side == 0: # bot to left
                        left = 1
                        if side_select == 0:
                            side = 2
                        if side_select == 1:
                            side = 3
                        if side_select == 2:
                            side = 4
                    elif side == 1: # bot to right
                        right = 1
                        if side_select == 0:
                            side = 2
                        if side_select == 1:
                            side = 3
                        if side_select == 2:
                            side = 4
                    elif side == 2: # bot to back
                        back = 1
                        if side_select == 0:
                            side = 0
                        if side_select == 1:
                            side = 1
                        if side_select == 2:
                            side = 4
                    elif side == 3: # bot to front
                        front = 1
                        if side_select == 0:
                            side = 0
                        if side_select == 1:
                            side = 1
                        if side_select == 2:
                            side = 4
                elif right == 1: # RIGHT
                    right = 0
                    if side == 4: # right to top
                        top = 1
                        if side_select == 0:
                            side = 2
                        if side_select == 1:
                            side = 3
                        if side_select == 2:
                            side = 0
                    elif side == 5: # right to bot
                        bot = 1
                        if side_select == 0:
                            side = 0
                        if side_select == 1:
                            side = 2
                        if side_select == 2:
                            side = 3
                    elif side == 2: # right to back
                        back = 1
                        if side_select == 0:
                            side = 0
                        if side_select == 1:
                            side = 5
                        if side_select == 2:
                            side = 4
                    elif side == 3: # right to front
                        front = 1
                        if side_select == 0:
                            side = 0
                        if side_select == 1:
                            side = 5
                        if side_select == 2:
                            side = 4
                elif left == 1: # LEFT
                    left = 0
                    if side == 4: # left to top
                        top = 1
                        if side_select == 0:
                            side = 3
                        if side_select == 1:
                            side = 2
                        if side_select == 2:
                            side = 1
                    elif side == 5: # left to bot
                        bot = 1
                        if side_select == 0:
                            side = 2
                        if side_select == 1:
                            side = 3
                        if side_select == 2:
                            side = 1
                    elif side == 2: # left to back
                        back = 1
                        if side_select == 0:
                            side = 1
                        if side_select == 1:
                            side = 5
                        if side_select == 2:
                            side = 4
                    elif side == 3: # left to front
                        front = 1
                        if side_select == 0:
                            side = 1
                        if side_select == 1:
                            side = 5
                        if side_select == 2:
                            side = 4
                elif front == 1: # front
                    front = 0
                    if side == 4: # front to top
                        top = 1
                        if side_select == 0:
                            side = 2
                        if side_select == 1:
                            side = 0
                        if side_select == 2:
                            side = 1
                    elif side == 5: # front to bot
                        bot = 1
                        if side_select == 0:
                            side = 0
                        if side_select == 1:
                            side = 2
                        if side_select == 2:
                            side = 1
                    elif side == 0: # front to left
                        left = 1
                        if side_select == 0:
                            side = 2
                        if side_select == 1:
                            side = 5
                        if side_select == 2:
                            side = 4
                    elif side == 1: # front to right
                        right = 1
                        if side_select == 0:
                            side = 2
                        if side_select == 1:
                            side = 5
                        if side_select == 2:
                            side = 4
                elif back == 1: # back
                    back = 0
                    if side == 4: # back to top
                        top = 1
                        if side_select == 0:
                            side = 3
                        if side_select == 1:
                            side = 0
                        if side_select == 2:
                            side = 1
                    elif side == 5: # back to bot
                        bot = 1
                        if side_select == 0:
                            side = 0
                        if side_select == 1:
                            side = 3
                        if side_select == 2:
                            side = 1
                    elif side == 0: # back to left
                        left = 1
                        if side_select == 0:
                            side = 3
                        if side_select == 1:
                            side = 5
                        if side_select == 2:
                            side = 4
                    elif side == 1: # back to right
                        right = 1
                        if side_select == 0:
                            side = 3
                        if side_select == 1:
                            side = 5
                        if side_select == 2:
                            side = 4

                for xx in range(0, 8):
                    oldpullback[xx] = 0
                    pullback[xx] = 0

                folderaddr[0] = -8
                folderaddr[1] = -7
                folderaddr[2] = -6
                folderaddr[3] = -5
                folderaddr[4] = -4
                folderaddr[5] = -3
                folderaddr[6] = -2
                folderaddr[7] = -1

        if folderaddr[7] != 7:
            for zz in range(0, 8):
                folderaddr[zz] = folderaddr[zz] + 1


class DoBouncySnakeAnimation(threading.Thread):
    def __init__(self, obj, *args, **kwargs):
        super(DoBouncySnakeAnimation, self).__init__(*args, **kwargs)
        self.obj = obj

    def run(self):
        bouncyvTwo(self.obj)


def bouncyvTwo(obj):
    wipex = 0
    wipey = 0
    wipez = 0
    ranr = 0
    rang = 0
    ranb = 0
    select = 0
    oldx = [0] * 50
    oldy = [0] * 50
    oldz = [0] * 50

    x = [0] * 50
    y = [0] * 50
    z = [0] * 50
    addr = 0
    ledcount = 20
    direct = 0
    direcTwo = 0
    xx = [0] * 50
    yy = [0] * 50
    zz = [0] * 50

    xbit = 1
    ybit = 1
    zbit = 1

    for addr in range(0, ledcount + 1):
        oldx[addr] = 0
        oldy[addr] = 0
        oldz[addr] = 0
        x[addr] = 0
        y[addr] = 0
        z[addr] = 0
        xx[addr] = 0
        yy[addr] = 0
        zz[addr] = 0

    frame = LEDFrame()
    start = current_milli_time()

    while (current_milli_time() - start) < TIME_FOR_1_ANIMATIONS_IN_MS:
        if obj.cube.abort_animation_thread:
            return

        direct = randint(0, 2)

        for addr in range(1, ledcount + 1):
          frame.turnOnLed(oldx[addr], oldy[addr], oldz[addr], 0, 0, 0)
          frame.turnOnLed(x[addr], y[addr], z[addr], xx[addr], yy[addr], zz[addr])

        for addr in range(1, ledcount + 1):
          oldx[addr] = x[addr]
          oldy[addr] = y[addr]
          oldz[addr] = z[addr]

        sendFrame(obj, frame)
        time.sleep(0.020)

        if direct == 0:
          x[0] = x[0] + xbit
        if direct == 1:
          y[0] = y[0] + ybit
        if direct == 2:
          z[0] = z[0] + zbit

        if direct == 3:
          x[0] = x[0] - xbit
        if direct == 4:
          y[0] = y[0] - ybit
        if direct == 5:
          z[0] = z[0] - zbit

        if x[0] > 7:
            xbit = -1
            x[0] = 7
            xx[0] = randint(0, 15)
            yy[0] = randint(0, 15)
            zz[0] = 0

        if x[0] < 0:
          xbit = 1
          x[0] = 0
          xx[0] = randint(0, 15)
          yy[0] = 0
          zz[0] = randint(0, 15)

        if y[0] > 7:
          ybit = -1
          y[0] = 7
          xx[0] = 0
          yy[0] = randint(0, 15)
          zz[0] = randint(0, 15)

        if y[0] < 0:
          ybit = 1
          y[0] = 0
          xx[0] = 0
          yy[0] = randint(0, 15)
          zz[0] = randint(0, 15)

        if z[0] > 7:
          zbit = -1
          z[0] = 7
          xx[0] = randint(0, 15)
          yy[0] = 0
          zz[0] = randint(0, 15)

        if z[0] < 0:
          zbit = 1
          z[0] = 0
          xx[0] = randint(0, 15)
          yy[0] = randint(0, 15)
          zz[0] = 0

        for addr in reversed(range(1, ledcount + 1)):
          x[addr] = x[addr - 1]
          y[addr] = y[addr - 1]
          z[addr] = z[addr - 1]
          xx[addr] = xx[addr - 1]
          yy[addr] = yy[addr - 1]
          zz[addr] = zz[addr - 1]


def rgb(minimum, maximum, value):
    minimum, maximum = float(minimum), float(maximum)
    ratio = 2 * (value-minimum) / (maximum - minimum)
    b = int(max(0, 255*(1 - ratio)))
    r = int(max(0, 255*(ratio - 1)))
    g = 255 - b - r
    return r, g, b


def translate(value, leftMin, leftMax, rightMin, rightMax):
    # Figure out how 'wide' each range is
    leftSpan = leftMax - leftMin
    rightSpan = rightMax - rightMin

    # Convert the left range into a 0-1 range (float)
    valueScaled = float(value - leftMin) / float(leftSpan)

    # Convert the 0-1 range into a value in the right range.
    return rightMin + (valueScaled * rightSpan)


class DoSpectrumAnimation(threading.Thread):
    def __init__(self, obj, *args, **kwargs):
        super(DoSpectrumAnimation, self).__init__(*args, **kwargs)
        self.obj = obj

    def run(self):
        run_pyaudio_fft_spectrum(self.obj, True)


def run_pyaudio_fft_spectrum(obj, infinite=False):
    visualize = 0
    ear = Stream_Analyzer(
        device=2,  # Pyaudio (portaudio) device index, defaults to first mic input
        rate=None,  # Audio samplerate, None uses the default source settings
        FFT_window_size_ms=60,  # Window size used for the FFT transform
        updates_per_second=1000,  # How often to read the audio stream for new data
        smoothing_length_ms=150,  # Apply some temporal smoothing to reduce noisy features
        n_frequency_bins=64,  # The FFT features are grouped in bins
        visualize=visualize,  # Visualize the FFT features with PyGame
        verbose=False,  # Print running statistics (latency, fps, ...)
        height=450,  # Height, in pixels, of the visualizer window,
        window_ratio=24/9  # Float ratio of the visualizer window. e.g. 24/9
    )

    fps = 50
    barsData = [0] * 64
    start_time = time.time()

    while True:
        current_time = time.time()
        if not infinite and (current_time - start_time > 5):
            return

        if obj.cube.abort_animation_thread:
            if visualize == 1:
                ear.visualizer.stop()
            return

        start_time_ms = current_milli_time()
        raw_fftx, raw_fft, binned_fftx, binned_fft = ear.get_audio_features()
        #print(max(binned_fft))

        for i, frequency in enumerate(binned_fftx):
            power = binned_fft[i]

            x = int(i / 8)
            y = i % 8

            max_power = 70 * 1000

            # TODO: automatic power translation
            if int(frequency) > 2500:
                max_power = 40 * 1000
            elif int(frequency) > 4000:
                max_power = 20 * 1000

            level = translate(power, 0, max_power, 0, 7)

            if level > 7:
                level = 7
            barsData[i] = int(level + 0.2)
            #frame.drawColumn(x, y, level, int(r / 17), int(g / 17), int(b / 17))

        sendSpectrum(obj, barsData)
        fft_duration_ms = current_milli_time() - start_time_ms

        if (fft_duration_ms / 1000) > (1. / fps):
            print('continue')
            time.sleep(0.002)
            continue

        time.sleep((1. / fps) - (fft_duration_ms / 1000))


if __name__ == '__main__':
    while 1:

        pass
        #start_spectrum(5000)
        #bouncyvTwo()
        #sinwaveTwo()
        #folder()
        #rainVersionTwo()
        #color_wheel()
        #testAudioSpectrum(infinite=True)
        #start_spectrum(TIME_FOR_1_ANIMATIONS_IN_MS)
        #brightness_3_colors()





