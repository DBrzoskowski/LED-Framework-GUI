import math

class Led:
    def __init__(self, *args):
        # one led 16 bits
        if len(args) == 3:
            self.red = format(min([args[0], 15]), '04b')
            self.green = format(min([args[1], 15]), '04b')
            self.blue = format(min([args[2], 15]), '04b')
        else:
            self.red = format(0, '04b')
            self.green = format(0, '04b')
            self.blue = format(0, '04b')

    def translateBinary(self):
        return f"{self.red}{self.green}{self.blue}"


class Layer:
    def __init__(self):
        self.leds = [Led() for _ in range(64)]

    def updateLed(self, led, position):
        self.leds[position] = led

    def translateBinary(self):
        layersBinary = ''
        for led in self.leds:
            layersBinary += led.translateBinary()
        return layersBinary


class Frame:
    def __init__(self):
        self.layers = [Layer() for _ in range(8)]

    def addLayer(self, layer, level):
        self.layers[level] = layer

    def setFrame(self, frame):
        self.layers = frame

    def translateBinary(self):
        framesBinary = ''
        for layer in self.layers:
            framesBinary += layer.translateBinary()
        return framesBinary

    def updateColumn(self, level, xCord, yCord, turnOn):
        """ view on top of matrix. Each 2x2 matrix will map one sound frequency range

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
        self.layers[level].updateLed(Led(brightness, brightness, brightness), pos_00)
        self.layers[level].updateLed(Led(brightness, brightness, brightness), pos_01)
        self.layers[level].updateLed(Led(brightness, brightness, brightness), pos_10)
        self.layers[level].updateLed(Led(brightness, brightness, brightness), pos_11)


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


def frequencyToMatrix(frequency):
    frequency_map = {0: {0, 0}, 1: {0, 1}, 2: {0, 2}, 3: {0, 3}, 4: {1, 0}, 5: {1, 1}, 6: {1, 2}, 7: {1, 3}, 8: {2, 0},
                     9: {2, 1}, 10: {2, 2}, 11: {2, 3}, 12: {2, 3}, 13: {3, 0}, 14: {3, 1}, 15: {3, 2}, 16: {3, 3}}
    matrixNumber = math.floor(min(frequency / 625, 16))
    return frequency_map[matrixNumber]


def spectrumVisualize(frame, frequency, power):
    xCord, yCord = frequencyToMatrix(frequency)
    for level in range(8):
        frame.updateColumn(level, xCord, yCord, level <= power)