import socket
import sys
from enum import Enum
import time
from random import *
from audio_spectrum import *

# CONFIG
MAX_PACKETS = 255

UDP_IP = "192.168.0.10"
UDP_PORT = 4210

TYPE_HEADER = 0xFE
TYPE_BODY = 0xBB


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

    def turnOnLed(self, x, y, z, r, g, b):
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
        print(f'Packet: {packet}')
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

    print(MESSAGE)

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # UDP

    sock.sendto(MESSAGE, (UDP_IP, UDP_PORT))


def sendBody(packet_to_send):
    body = LEDBody(packet_to_send)

    MESSAGE = body.constructPacket()
    print(MESSAGE)

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


def sendFrame(frame_to_send):
    sendHeader(frame_to_send)
    sendBodies(frame_to_send)

    # send header
    # send bodies


def current_milli_time():
    return round(time.time() * 1000)


def color_wheel():
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

    while current_milli_time() - start < 15000:
        swiper = randint(0, 3)
        ranx = randint(0, 16)
        rany = randint(0, 16)

        for xx in range(0, 8):
            for yy in range(0, 8):
                for zz in range(0, 8):
                    frame.turnOnLed(xx, yy, zz, ranx, 0, rany)
            sendFrame(frame)
            time.sleep(0.050)

        ranx = randint(0, 16)
        rany = randint(0, 16)

        for xx in reversed(range(0, 8)) :
            for yy in range(0, 8):
                for zz in range(0, 8):
                    frame.turnOnLed(xx, yy, zz, ranx, rany, 0)
            sendFrame(frame)
            time.sleep(0.050)

        ranx = randint(0, 16)
        rany = randint(0, 16)

        for xx in range(0, 8):
            for yy in range(0, 8):
                for zz in range(0, 8):
                    frame.turnOnLed(xx, yy, zz, 0, ranx, rany)
            sendFrame(frame)
            time.sleep(0.050)

        ranx = randint(0, 16)
        rany = randint(0, 16)
        for xx in reversed(range(0, 8)) :
            for yy in range(0, 8):
                for zz in range(0, 8):
                    frame.turnOnLed(xx, yy, zz, ranx, rany, 0)
            sendFrame(frame)
            time.sleep(0.050)


def brightness_3_colors():
    frame = LEDFrame()
    delay = 0.25

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


def sinwaveTwo():
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

    while (current_milli_time() - start) < 15000:
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

        sendFrame(frame)
        time.sleep(0.050)
        frame.clear()


def rainVersionTwo():
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

    while (current_milli_time() - start) < 20000:
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

        time.sleep(0.04)
        sendFrame(frame)

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


def folder():
    xx, yy, zz,  = 0,0,0
    pullback = []
    state = 0
    backorfront = 7

    folderaddr = []
    LED_Old = []
    oldpullback = []
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

    frame = LEDFrame()

    for xx in range(8):
        oldpullback[xx] = 0
        pullback[xx] = 0

    start = current_milli_time()
    while current_milli_time() - start < 10000:
        if top == 1:
            if side == 0:
                #top to left-side
                for yy in range(8):
                    for xx in range(8):
                        frame.turnOnLed(yy - oldpullback[yy], xx, 7 - LED_Old[yy], 0, 0, 0)
                        frame.turnOnLed(yy - pullback[yy], xx, 7 - folderaddr[yy], ranx, rany, ranz)
            if side == 2:
                #top to back-side
                for yy in range(8):
                    for  xx in range(8):
                        frame.turnOnLed(xx, yy - oldpullback[yy], 7 - LED_Old[yy], 0, 0, 0)
                        frame.turnOnLed(xx, yy - pullback[yy], 7 - folderaddr[yy], ranx, rany, ranz)

            if side == 3:
                #top-side to front-side
                for yy in range(8):
                    for xx in range(8):
                        LED(xx, yy + oldpullback[yy], 7 - LED_Old[7 - yy], 0, 0, 0)
                        LED(xx, yy + pullback[yy], 7 - folderaddr[7 - yy], ranx, rany, ranz)

            if side == 1:
                #top-side to right
                for yy in range(8):
                    for xx in range(8):
                        frame.turnOnLed(yy + oldpullback[yy], xx, 7 - LED_Old[7 - yy], 0, 0, 0)
                        frame.turnOnLed(yy + pullback[yy], xx, 7 - folderaddr[7 - yy], ranx, rany, ranz)

         #top

        if right == 1:
            if side == 4:
                #right-side to top
                for yy in range(8):
                    for xx in range(8):
                        frame.turnOnLed(7 - LED_Old[7 - yy], xx, yy + oldpullback[7 - yy], 0, 0, 0)
                        frame.turnOnLed(7 - folderaddr[7 - yy], xx, yy + pullback[7 - yy], ranx, rany, ranz)

            if side == 3:
                #right-side to front-side
                for yy in range(8):
                    for xx in range(8):
                        frame.turnOnLed(7 - LED_Old[7 - yy], yy + oldpullback[yy], xx, 0, 0, 0)
                        frame.turnOnLed(7 - folderaddr[7 - yy], yy + pullback[yy], xx, ranx, rany, ranz)

            if side == 2:
                #right-side to back-side
                for yy in range(8):
                    for xx in range(8):
                        frame.turnOnLed(7 - LED_Old[yy], yy - oldpullback[yy], xx, 0, 0, 0)
                        frame.turnOnLed(7 - folderaddr[yy], yy - pullback[yy], xx, ranx, rany, ranz)

            if side == 5:
                #right-side to bottom
                for yy in range(8):
                    for  xx in range(8):
                        frame.turnOnLed(7 - LED_Old[yy], xx, yy - oldpullback[yy], 0, 0, 0)
                        frame.turnOnLed(7 - folderaddr[yy], xx, yy - pullback[yy], ranx, rany, ranz)
        #right

        if left == 1:
            if side == 4:
                #left-side to top
                for yy in range(8):
                    for  xx in range(8):
                        frame.turnOnLed(LED_Old[7 - yy], xx, yy + oldpullback[yy], 0, 0, 0)
                        frame.turnOnLed(folderaddr[7 - yy], xx, yy + pullback[yy], ranx, rany, ranz)

            if side == 3:
                #left-side to front-side
                for yy in range(8):
                    for  xx in range(8):
                        frame.turnOnLed(LED_Old[7 - yy], yy + oldpullback[yy], xx, 0, 0, 0)
                        frame.turnOnLed(folderaddr[7 - yy], yy + pullback[yy], xx, ranx, rany, ranz)

            if side == 2:
                #left-side to back-side
                for yy in range(8):
                    for  xx in range(8):
                        frame.turnOnLed(LED_Old[yy], yy - oldpullback[yy], xx, 0, 0, 0)
                        frame.turnOnLed(folderaddr[yy], yy - pullback[yy], xx, ranx, rany, ranz)

            if side == 5:
                #left-side to bottom
                for yy in range(8):
                    for  xx in range(8):
                        frame.turnOnLed(LED_Old[yy], xx, yy - oldpullback[yy], 0, 0, 0)
                        frame.turnOnLed(folderaddr[yy], xx, yy - pullback[yy], ranx, rany, ranz)

         #left

        if back == 1:
            if side == 1:
                #back-side to right-side
                for yy in range(8):
                    for  xx in range(8):
                        frame.turnOnLed(yy + oldpullback[yy], LED_Old[7 - yy], xx, 0, 0, 0)
                        frame.turnOnLed(yy + pullback[yy], folderaddr[7 - yy], xx, ranx, rany, ranz)

            if side == 4:
                # back-side to top-side
                for yy in range(8):
                    for  xx in range(8):
                        frame.turnOnLed(xx, LED_Old[7 - yy], yy + oldpullback[yy], 0, 0, 0)
                        frame.turnOnLed(xx, folderaddr[7 - yy], yy + pullback[yy], ranx, rany, ranz)

            if side == 5:
                # back-side to bottom
                for yy in range(8):
                    for  xx in range(8):
                        frame.turnOnLed(xx, LED_Old[yy], yy - oldpullback[yy], 0, 0, 0)
                        frame.turnOnLed(xx, folderaddr[yy], yy - pullback[yy], ranx, rany, ranz)
 #state1
            if side == 0:
                #back-side to left-side
                for yy in range(8):
                    for  xx in range(8):
                        frame.turnOnLed(yy - oldpullback[yy], LED_Old[yy], xx, 0, 0, 0)
                        frame.turnOnLed(yy - pullback[yy], folderaddr[yy], xx, ranx, rany, ranz)
 #back
        if bot == 1:
            if side == 1:
                # bottom-side to right-side
                for yy in range(8):
                    for  xx in range(8):
                        frame.turnOnLed(yy + oldpullback[yy], xx, LED_Old[7 - yy], 0, 0, 0)
                        frame.turnOnLed(yy + pullback[yy], xx, folderaddr[7 - yy], ranx, rany, ranz)

            if side == 3:
                #bottom to front-side
                for yy in range(8):
                    for  xx in range(8):
                        frame.turnOnLed(xx, yy + oldpullback[yy], LED_Old[7 - yy], 0, 0, 0)
                        frame.turnOnLed(xx, yy + pullback[yy], folderaddr[7 - yy], ranx, rany, ranz)

            if side == 2:
                #bottom to back-side
                for yy in range(8):
                    for  xx in range(8):
                        frame.turnOnLed(xx, yy - oldpullback[yy], LED_Old[yy], 0, 0, 0)
                        frame.turnOnLed(xx, yy - pullback[yy], folderaddr[yy], ranx, rany, ranz)

            if side == 0:
                #bottom to left-side
                for yy in range(8):
                    for  xx in range(8):
                        frame.turnOnLed(yy - oldpullback[yy], xx, LED_Old[yy], 0, 0, 0)
                        frame.turnOnLed(yy - pullback[yy], xx, folderaddr[yy], ranx, rany, ranz)

         #bot

        if front == 1:
            if side == 0:
                #front-side to left-side
                for yy in range(8):
                    for  xx in range(8):
                        frame.turnOnLed(yy - oldpullback[yy], 7 - LED_Old[yy], xx, 0, 0, 0)
                        frame.turnOnLed(yy - pullback[yy], 7 - folderaddr[yy], xx, ranx, rany, ranz)

            if side == 5:
                # front-side to bottom
                for yy in range(8):
                    for xx in range(8):
                        frame.turnOnLed(xx, 7 - LED_Old[yy], yy - oldpullback[yy], 0, 0, 0)
                        frame.turnOnLed(xx, 7 - folderaddr[yy], yy - pullback[yy], ranx, rany, ranz)

            if side == 4:
                # front-side to top-side
                for yy in range(8):
                    for xx in range(8):
                        frame.turnOnLed(xx, 7 - LED_Old[7 - yy], yy + oldpullback[yy], 0, 0, 0)
                        LED(xx, 7 - folderaddr[7 - yy], yy + pullback[yy], ranx, rany, ranz)

            if side == 1:
                #front-side to right-side
                for yy in range(8):
                    for xx in range(8):
                        frame.turnOnLed(yy + oldpullback[yy], 7 - LED_Old[7 - yy], xx, 0, 0, 0)
                        frame.turnOnLed(yy + pullback[yy], 7 - folderaddr[7 - yy], xx, ranx, rany, ranz)

         #front

        time.sleep(5) #               time.sleep   time.sleep  time.sleep
        for  xx in range(8):
            LED_Old[xx] = folderaddr[xx]
            oldpullback[xx] = pullback[xx]


        if folderaddr[7] == 7:
            # pullback=8
            for  zz in range(8):
                pullback[zz] = pullback[zz] + 1

            if pullback[7] == 8: #finished with fold
                time.sleep(10)
                #state++
                #if(state==4)
                #state=0

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


                side_select = randint(0,2)

                if top == 1: #                 TOP
                    top = 0
                    if side == 0: #top to left
                        left = 1
                        if side_select == 0:
                            side = 2
                        if side_select == 1:
                            side = 3
                        #ifside_select==2) side=4
                        if side_select == 2:
                            side = 5

                    else:
                        if side == 1: #top to right
                            right = 1
                            if side_select == 0:
                                side = 5
                            if side_select == 1:
                                side = 2
                            if side_select == 2:
                                side = 3
                            #ifside_select==3) side=4

                        else:
                            if side == 2: #top to back
                                back = 1
                                if side_select == 0:
                                    side = 0
                                if side_select == 1:
                                    side = 1
                                if side_select == 2:
                                    side = 5
                                #ifside_select==3) side=4

                            else:
                                if side == 3: #top to front
                                    front = 1
                                    if side_select == 0:
                                        side = 0
                                    if side_select == 1:
                                        side = 1
                                    if side_select == 2:
                                        side = 5
                                    #ifside_select==3) side=4
                else: #top
                    if bot == 1: #                 BOTTOM
                        bot = 0
                        if side == 0: #bot to left
                            left = 1
                            if side_select == 0:
                                side = 2
                            if side_select == 1:
                                side = 3
                            if side_select == 2:
                                side = 4
                            #ifside_select==3) side=5

                        else:
                            if side == 1: #bot to right
                                right = 1
                                #ifside_select==0) side=5
                                if side_select == 0:
                                    side = 2
                                if side_select == 1:
                                    side = 3
                                if side_select == 2:
                                    side = 4

                            else:
                                if side == 2: #bot to back
                                    back = 1
                                    if side_select == 0:
                                        side = 0
                                    if side_select == 1:
                                        side = 1
                                    #ifside_select==2) side=5
                                    if side_select == 2:
                                        side = 4

                                else:
                                    if side == 3: #bot to front
                                        front = 1
                                        if side_select == 0:
                                            side = 0
                                        if side_select == 1:
                                            side = 1
                                        #ifside_select==2) side=5
                                        if side_select == 2:
                                            side = 4
                    else: #bot
                        if right == 1: #                 RIGHT
                            right = 0
                            if side == 4: #right to top
                                top = 1
                                if side_select == 0:
                                    side = 2
                                if side_select == 1:
                                    side = 3
                                if side_select == 2:
                                    side = 0
                                #ifside_select==3) side=1
                            else:
                                if side == 5: #right to bot
                                    bot = 1
                                    if side_select == 0:
                                        side = 0
                                    if side_select == 1:
                                        side = 2
                                    if side_select == 2:
                                        side = 3
                                    #ifside_select==3) side=1
                                else:
                                    if side == 2: #right to back
                                        back = 1
                                        if side_select == 0:
                                            side = 0
                                        #ifside_select==1) side=1
                                        if side_select == 1:
                                            side = 5
                                        if side_select == 2:
                                            side = 4
                                    else:
                                        if side == 3: #right to front
                                            front = 1
                                            if side_select == 0:
                                                side = 0
                                            #ifside_select==1) side=1
                                            if side_select == 1:
                                                side = 5
                                            if side_select == 2:
                                                side = 4
                        else: #bot
                            if left == 1: #                 LEFT
                                left = 0
                                if side == 4: #left to top
                                    top = 1
                                    #ifside_select==0) side=2
                                    if side_select == 0:
                                        side = 3
                                    if side_select == 1:
                                        side = 2
                                    if side_select == 2:
                                        side = 1
                                else:
                                    if side == 5: #left to bot
                                        bot = 1
                                        #ifside_select==0) side=0
                                        if side_select == 0:
                                            side = 2
                                        if side_select == 1:
                                            side = 3
                                        if side_select == 2:
                                            side = 1
                                    else:
                                        if side == 2: #left to back
                                            back = 1
                                            #ifside_select==0) side=0
                                            if side_select == 0:
                                                side = 1
                                            if side_select == 1:
                                                side = 5
                                            if side_select == 2: side = 4
                                        else:
                                            if side == 3: #left to front
                                                front = 1
                                                #ifside_select==0) side=0
                                                if side_select == 0:
                                                    side = 1
                                                if side_select == 1:
                                                    side = 5
                                                if side_select == 2: side = 4
                            else: #bot
                                if front == 1: #                 front
                                    front = 0
                                    if side == 4: #front to top
                                        top = 1
                                        if side_select == 0:
                                            side = 2
                                        #ifside_select==1) side=3
                                        if side_select == 1:
                                            side = 0
                                        if side_select == 2:
                                            side = 1
                                    else:
                                        if side == 5: #front to bot
                                            bot = 1
                                            if side_select == 0:
                                                side = 0
                                            if side_select == 1:
                                                side = 2
                                            #ifside_select==2) side=3
                                            if side_select == 2: side = 1
                                        else:
                                            if side == 0: #front to left
                                                left = 1
                                                if side_select == 0:
                                                    side = 2
                                                # ifside_select==1) side=3
                                                if side_select == 1:
                                                    side = 5
                                                if side_select == 2:
                                                    side = 4
                                            else:
                                                if side == 1: #front to right
                                                    right = 1
                                                    if side_select == 0:
                                                        side = 2
                                                    # ifside_select==1) side=3
                                                    if side_select == 1:
                                                        side = 5
                                                    if side_select == 2:
                                                        side = 4
                                else: #bot
                                    if back == 1:
                                        back = 0
                                        if side == 4: #back to top
                                            top = 1
                                            #ifside_select==0) side=2
                                            if side_select == 0:
                                                side = 3
                                            if side_select == 1:
                                                side = 0
                                            if side_select == 2:
                                                side = 1
                                        else:
                                            if side == 5: #back to bot
                                                bot = 1
                                                if side_select == 0:
                                                    side = 0
                                                #ifside_select==1) side=2
                                                if side_select == 1:
                                                    side = 3
                                                if side_select == 2:
                                                    side = 1
                                            else:
                                                if side == 0: #back to left
                                                    left = 1
                                                    #ifside_select==0) side=2
                                                    if side_select == 0:
                                                        side = 3
                                                    if side_select == 1:
                                                        side = 5
                                                    if side_select == 2:
                                                        side = 4
                                                else:
                                                    if side == 1: #back to right
                                                        right = 1
                                                        #ifside_select==0) side=2
                                                        if side_select == 0:
                                                            side = 3
                                                        if side_select == 1:
                                                            side = 5
                                                        if side_select == 2:
                                                            side = 4

                    for xx in range(8):
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
            for zz in range(8):
                folderaddr[zz] = folderaddr[zz] + 1




def start_spectrum():
    visualiser = SpectrumVisualizer()
    visualiser.startVisualisation()


def folder2(): #****folder****folder****folder****folder****folder****folder****folder****folder****folder
    frame = LEDFrame()
    xx, yy, zz = 0
    pullback = []
    state = 0
    backorfront = 7 #backorfront 7 for back 0 for front

    folderaddr = []
    LED_Old = []
    oldpullback = []
    ranx = randint(0,15)
    rany = randint(0,15)
    ranz = randint(0,15)
    ranselect = 0
    bot = 0
    top = 1
    right, left, back, front, side, side_select = 0

    folderaddr[0] = -7
    folderaddr[1] = -6
    folderaddr[2] = -5
    folderaddr[3] = -4
    folderaddr[4] = -3
    folderaddr[5] = -2
    folderaddr[6] = -1
    folderaddr[7] = 0

    for xx in range(8):
        oldpullback[xx] = 0
        pullback[xx] = 0


    start = current_milli_time()
    while (current_milli_time() - start) < 10000:
        if top == 1:
            if side == 0:
                #top to left-side
                for yy in range(8):
                    for xx in range(8):
                        frame.turnOnLed(7 - LED_Old[yy], yy - oldpullback[yy], xx, 0, 0, 0);
                        frame.turnOnLed(7 - folderaddr[yy], yy - pullback[yy], xx, ranx, rany, ranz);

            if side == 2:
                #top to back-side
                for yy in range(8):
                    for xx in range(8):
                        frame.turnOnLed(7 - LED_Old[yy], xx, yy - oldpullback[yy], 0, 0, 0);
                        frame.turnOnLed(7 - folderaddr[yy], xx, yy - pullback[yy], ranx, rany, ranz);

            if side == 3:
                #top-side to front-side
                for yy in range(8):
                    for xx in range(8):
                        frame.turnOnLed(7 - LED_Old[7 - yy], xx, yy + oldpullback[yy], 0, 0, 0);
                        frame.turnOnLed(7 - folderaddr[7 - yy], xx, yy + pullback[yy], ranx, rany, ranz);

            if side == 1:
                #top-side to right
                for yy in rnage(8):
                    for xx in range(8):
                        frame.turnOnLed(7 - LED_Old[7 - yy], yy + oldpullback[yy], xx, 0, 0, 0);
                        frame.turnOnLed(7 - folderaddr[7 - yy], yy + pullback[yy], xx, ranx, rany, ranz);
          #top

        if right == 1:
            if side == 4:
                #right-side to top
                for yy in range(8):
                    for xx in range(8):
                        frame.turnOnLed(yy + oldpullback[7 - yy], 7 - LED_Old[7 - yy], xx, 0, 0, 0);
                        frame.turnOnLed(yy + pullback[7 - yy], 7 - folderaddr[7 - yy], xx, ranx, rany, ranz);

            if side == 3:
                #right-side to front-side
                for yy in range(8):
                    for xx in range(8):
                        frame.turnOnLed(xx, 7 - LED_Old[7 - yy], yy + oldpullback[yy], 0, 0, 0);
                        frame.turnOnLed(xx, 7 - folderaddr[7 - yy], yy + pullback[yy], ranx, rany, ranz);

            if side == 2:
                #right-side to back-side
                for yy in range(8):
                    for xx in range(8):
                        frame.turnOnLed(xx, 7 - LED_Old[yy], yy - oldpullback[yy], 0, 0, 0);
                        frame.turnOnLed(xx, 7 - folderaddr[yy], yy - pullback[yy], ranx, rany, ranz);

            if side == 5:
                #right-side to bottom
                for yy in range(8):
                    for xx in range(8):
                        frame.turnOnLed(yy - oldpullback[yy], 7 - LED_Old[yy], xx, 0, 0, 0);
                        frame.turnOnLed(yy - pullback[yy], 7 - folderaddr[yy], xx, ranx, rany, ranz);
         #right

        if left == 1:
            if side == 4:
                #left-side to top
                for yy in range(8):
                    for xx in range(8):
                        frame.turnOnLed(yy + oldpullback[yy], LED_Old[7 - yy], xx, 0, 0, 0);
                        frame.turnOnLed(yy + pullback[yy], folderaddr[7 - yy], xx, ranx, rany, ranz);

            if side == 3:
                #left-side to front-side
                for yy in range(8):
                    for xx in range(8):
                        frame.turnOnLed(xx, LED_Old[7 - yy], yy + oldpullback[yy], 0, 0, 0);
                        frame.turnOnLed(xx, folderaddr[7 - yy], yy + pullback[yy], ranx, rany, ranz);

            if side == 2:
                #left-side to back-side
                for yy in range(8):
                    for xx in range(8):
                        frame.turnOnLed(xx, LED_Old[yy], yy - oldpullback[yy], 0, 0, 0);
                        frame.turnOnLed(xx, folderaddr[yy], yy - pullback[yy], ranx, rany, ranz);

            if side == 5:
                #left-side to bottom
                for yy in range(8):
                    for xx in range(8):
                        frame.turnOnLed(yy - oldpullback[yy], LED_Old[yy], xx, 0, 0, 0);
                        frame.turnOnLed(yy - pullback[yy], folderaddr[yy], xx, ranx, rany, ranz);
          #left

        if back == 1:
            if side == 1:
                #back-side to right-side
                for yy in range(8):
                    for xx in range(8):
                        frame.turnOnLed(xx, yy + oldpullback[yy], LED_Old[7 - yy], 0, 0, 0);
                        frame.turnOnLed(xx, yy + pullback[yy], folderaddr[7 - yy], ranx, rany, ranz);

            if side == 4:
                # back-side to top-side
                for yy in range(8):
                    for xx in range(8):
                        frame.turnOnLed(yy + oldpullback[yy], xx, LED_Old[7 - yy], 0, 0, 0);
                        frame.turnOnLed(yy + pullback[yy], xx, folderaddr[7 - yy], ranx, rany, ranz);

            if side == 5:
                # back-side to bottom
                for yy in range(8):
                    for xx in range(8):
                        frame.turnOnLed(yy - oldpullback[yy], xx, LED_Old[yy], 0, 0, 0);
                        frame.turnOnLed(yy - pullback[yy], xx, folderaddr[yy], ranx, rany, ranz);
            #state1
            if side == 0:
                #back-side to left-side
                for yy in range(8):
                    for xx in range(8):
                        frame.turnOnLed(xx, yy - oldpullback[yy], LED_Old[yy], 0, 0, 0);
                        frame.turnOnLed(xx, yy - pullback[yy], folderaddr[yy], ranx, rany, ranz);
        #back
        if bot == 1:
            if side == 1:
                #bottom-side to right-side
                for yy in range(8):
                    for xx in range(8):
                        frame.turnOnLed(LED_Old[7 - yy], yy + oldpullback[yy], xx, 0, 0, 0);
                        frame.turnOnLed(folderaddr[7 - yy], yy + pullback[yy], xx, ranx, rany, ranz);

            if side == 3:
                #bottom to front-side
                for yy in range(8):
                    for xx in range(8):
                        frame.turnOnLed(LED_Old[7 - yy], xx, yy + oldpullback[yy], 0, 0, 0);
                        frame.turnOnLed(folderaddr[7 - yy], xx, yy + pullback[yy], ranx, rany, ranz);

            if side == 2:
                #bottom to back-side
                for yy in range(8):
                    for xx in range(8):
                        frame.turnOnLed(LED_Old[yy], xx, yy - oldpullback[yy], 0, 0, 0);
                        frame.turnOnLed(folderaddr[yy], xx, yy - pullback[yy], ranx, rany, ranz);

            if side == 0:
                #bottom to left-side
                for yy in range(8):
                    for xx in range(8):
                        frame.turnOnLed(LED_Old[yy], yy - oldpullback[yy], xx, 0, 0, 0);
                        frame.turnOnLed(folderaddr[yy], yy - pullback[yy], xx, ranx, rany, ranz);
        #bot

        if front == 1:
            if side == 0:
                #front-side to left-side
                for yy in range(8):
                    for xx in range(8):
                        frame.turnOnLed(xx, yy - oldpullback[yy], 7 - LED_Old[yy], 0, 0, 0);
                        frame.turnOnLed(xx, yy - pullback[yy], 7 - folderaddr[yy], ranx, rany, ranz);

            if side == 5:
                #front-side to bottom
                for yy in range(8):
                    for xx in range(8):
                        frame.turnOnLed(yy - oldpullback[yy], xx, 7 - LED_Old[yy], 0, 0, 0);
                        frame.turnOnLed(yy - pullback[yy], xx, 7 - folderaddr[yy], ranx, rany, ranz);

            if side == 4:
                #front-side to top-side
                for yy in range(8):
                    for xx in range(8):
                        frame.turnOnLed(yy + oldpullback[yy], xx, 7 - LED_Old[7 - yy], 0, 0, 0);
                        frame.turnOnLed(yy + pullback[yy], xx, 7 - folderaddr[7 - yy], ranx, rany, ranz);

            if side == 1:
                #front-side to right-side
                for yy in range(8):
                    for xx in range(8):
                        frame.turnOnLed(xx, yy + oldpullback[yy], 7 - LED_Old[7 - yy], 0, 0, 0);
                        frame.turnOnLed(xx, yy + pullback[yy], 7 - folderaddr[7 - yy], ranx, rany, ranz);

        #front

        sleep(5)
        for xx in range(8):
            LED_Old[xx] = folderaddr[xx]
            oldpullback[xx] = pullback[xx]

        if folderaddr[7] == 7:
            for zz in range(8):
                pullback[zz] = pullback[zz] + 1

            if pullback[7] == 8:
                sleep(10)

                ranselect = randint(0,2)
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

                side_select = randint(2)

                if top == 1: #                 TOP
                    top = 0
                    if side == 0: #top to left
                        left = 1
                        if side_select == 0:
                            side = 2
                        if side_select == 1:
                            side = 3
                        if side_select == 2:
                            side = 5
                    else:
                        if side == 1:#top to right
                            right = 1
                            if side_select == 0:
                                side = 5
                            if side_select == 1:
                                side = 2
                            if side_select == 2:
                                side = 3
                        else:
                            if side == 2:#top to back
                                back = 1
                                if side_select == 0:
                                    side = 0
                                if side_select == 1:
                                    side = 1
                                if side_select == 2:
                                    side = 5

                            else:
                                if side == 3:#top to front
                                    front = 1
                                    if side_select == 0:
                                        side = 0
                                    if side_select == 1:
                                        side = 1
                                    if side_select == 2:
                                        side = 5

                else: #top
                    if bot == 1:#                 BOTTOM
                        bot = 0
                        if side == 0:#bot to left
                            left = 1
                            if side_select == 0:
                                side = 2
                            if side_select == 1:
                                side = 3
                            if side_select == 2:
                                side = 4

                        else:
                            if side == 1: #bot to right
                                right = 1
                                if side_select == 0:
                                    side = 2
                                if side_select == 1:
                                    side = 3
                                if side_select == 2:
                                    side = 4

                            else:
                                if side == 2: #bot to back
                                    back = 1
                                    if side_select == 0:
                                        side = 0
                                    if side_select == 1:
                                        side = 1
                                    if side_select == 2:
                                        side = 4

                                else:
                                    if side == 3: #bot to front
                                        front = 1
                                        if side_select == 0:
                                            side = 0
                                        if side_select == 1:
                                            side = 1
                                        if side_select == 2:
                                            side = 4

                    else: #bot
                        if right == 1:#                 RIGHT
                            right = 0
                            if side == 4:#right to top
                                top = 1
                                if side_select == 0:
                                    side = 2
                                if side_select == 1:
                                    side = 3
                                if side_select == 2:
                                    side = 0
                            else:
                                if side == 5:#right to bot
                                    bot = 1
                                    if side_select == 0:
                                        side = 0
                                    if side_select == 1:
                                        side = 2
                                    if side_select == 2:
                                        side = 3
                                else:
                                    if side == 2:#right to back
                                        back = 1
                                        if side_select == 0:
                                            side = 0
                                        if side_select == 1:
                                            side = 5
                                        if side_select == 2:
                                            side = 4
                                    else:
                                        if side == 3:#right to front
                                            front = 1
                                            if side_select == 0:
                                                side = 0
                                            if side_select == 1:
                                                side = 5
                                            if side_select == 2:
                                                side = 4

                        else: #bot
                            if left == 1: #                 LEFT
                                left = 0
                                if side == 4:#left to top
                                    top = 1
                                    if side_select == 0:
                                        side = 3
                                    if side_select == 1:
                                        side = 2
                                    if side_select == 2:
                                        side = 1

                                else:
                                    if side == 5:#left to bot
                                        bot = 1
                                        if side_select == 0:
                                            side = 2
                                        if side_select == 1:
                                            side = 3
                                        if side_select == 2:
                                            side = 1

                                    else:
                                        if side == 2:#left to back
                                            back = 1
                                            if side_select == 0:
                                                side = 1
                                            if side_select == 1:
                                                side = 5
                                            if side_select == 2:
                                                side = 4

                                        else:
                                            if side == 3:#left to front
                                                front = 1
                                                if side_select == 0:
                                                    side = 1
                                                if side_select == 1:
                                                    side = 5
                                                if side_select == 2:
                                                    side = 4


                            else: #bot
                                if front == 1:#                 front
                                    front = 0
                                    if side == 4:#front to top
                                        top = 1
                                        if side_select == 0:
                                            side = 2
                                        if side_select == 1:
                                            side = 0
                                        if side_select == 2:
                                            side = 1

                                    else:
                                        if side == 5:#front to bot
                                            bot = 1
                                            if side_select == 0:
                                                side = 0
                                            if side_select == 1:
                                                side = 2
                                            if side_select == 2:
                                                side = 1

                                        else:
                                            if side == 0:#front to left
                                                left = 1
                                                if side_select == 0:
                                                    side = 2
                                                if side_select == 1:
                                                    side = 5
                                                if side_select == 2:
                                                    side = 4

                                            else:
                                                if side == 1:#front to right
                                                    right = 1
                                                    if side_select == 0:
                                                        side = 2
                                                    if side_select == 1:
                                                        side = 5
                                                    if side_select == 2:
                                                        side = 4


                                else: #bot
                                    if back == 1:#                 back
                                        back = 0
                                        if side == 4: #back to top
                                            top = 1
                                            if side_select == 0:
                                                side = 3
                                            if side_select == 1:
                                                side = 0
                                            if side_select == 2:
                                                side = 1

                                        else:
                                            if side == 5:#back to bot
                                                bot = 1
                                                if side_select == 0:
                                                    side = 0
                                                if side_select == 1:
                                                    side = 3
                                                if side_select == 2:
                                                    side = 1

                                            else:
                                                if side == 0:#back to left
                                                    left = 1
                                                    if side_select == 0:
                                                        side = 3
                                                    if side_select == 1:
                                                        side = 5
                                                    if side_select == 2:
                                                        side = 4

                                                else:
                                                    if side == 1:#back to right
                                                        right = 1
                                                        if side_select == 0:
                                                            side = 3
                                                        if side_select == 1:
                                                            side = 5
                                                        if side_select == 2:
                                                            side = 4

                                    #bot


                for xx in range(8):
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
            for zz in range(8):
                folderaddr[zz] = folderaddr[zz] + 1

if __name__ == '__main__':
    #start_spectrum()
    rainVersionTwo()
    sinwaveTwo()
    color_wheel()
    brightness_3_colors()
    folder()



