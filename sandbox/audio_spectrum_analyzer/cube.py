import math


class Led:
    def __init__(self, *args):
        # one led 16 bits
        if len(args) == 3:
            self.led = [format(min([args[_], 15]), '04b') for _ in range(3)]
        else:
            self.led = [format(0, '04b') for _ in range(3)]

    # color: 1 - red, 2 - green, 3 - blue
    def translateBinary(self, color):
        return f"{self.led[color]}"


class Layer:
    def __init__(self):
        self.leds = [Led() for _ in range(64)]

    def updateLed(self, led, position):
        self.leds[position] = led

    def translateBinary(self, color):
        colorBinary = ''
        for led in self.leds:
            colorBinary += led.translateBinary(color)
        return colorBinary

class Frame:
    def __init__(self):
        self.layers = [Layer() for _ in range(8)]

    def addLayer(self, layer, level):
        self.layers[level] = layer

    def setFrame(self, frame):
        self.layers = frame

    def translateBinary(self):
        framesBinary = ''
        for color in range(3):
            for bamBit in reversed(range(4)):
                for layer in self.layers:
                    framesBinary += layer.translateBinary(color, bamBit)

            #for layer in self.layers:
            #    framesBinary += layer.translateBinary(color)

        return framesBinary

    def updateColumn(self, level, xCord, yCord, turnOn):
        """ view from top of the matrix. Each 2x2 matrix will map one sound frequency range

                            00 01
                            10 11

           0    1        2   3       4   5       6    7
           8    9       10  11      12  13      14   15

           16  17       18  19      20  21      22   23
           24  25       26  27      28  29      30   31

           32  33       34  35      36  37      38   39
           40  41       42  43      44  45      46   47

           48  49       50  51      52  53      54   55
           56  57       58  59      60  61      62   63

           """
        pos_00 = 0 + xCord * 2 + (yCord * 16)
        pos_01 = 1 + xCord * 2 + (yCord * 16)
        pos_10 = 8 + xCord * 2 + (yCord * 16)
        pos_11 = 9 + xCord * 2 + (yCord * 16)

        if turnOn:
            brightness = 15
        else:
            brightness = 0

        # this should be modified to contain color values
        self.layers[level].updateLed(Led(brightness, 0, 0), pos_00)
        self.layers[level].updateLed(Led(brightness, 0, 0), pos_01)
        self.layers[level].updateLed(Led(brightness, 0, 0), pos_10)
        self.layers[level].updateLed(Led(brightness, 0, 0), pos_11)


class Animation:
    def __init__(self):
        self.frames = []

    def addFrame(self, frame):
        self.frames.append(frame)

    def translateBinary(self):
        animationBinary = ''
        for frame in self.frames:
            animationBinary = frame.translateBinary()
        return animationBinary
