class Led:
    def __init__(self):
        # one led 32 bits
        self.red = format(0, '08b')
        self.green = format(0, '08b')
        self.blue = format(0, '08b')
        self.brightness = format(0, '08b')

    def updateLed(self, red, green, blue, brightness):
        self.red = format(min([red, 255]), '08b')
        self.green = format(min([green, 255]), '08b')
        self.blue = format(min([blue, 255]), '08b')
        self.brightness = format(min([brightness, 15]), '08b')

    def updateBrightness(self, brightness):
        self.brightness = format(min([brightness, 15]), '08b')

    def offLed(self):
        self.brightness = format(0, '04b')

    def translateBinary(self):
        return f"{self.red}{self.green}{self.blue}{self.brightness}"


class Layer:
    def __init__(self):
        # layer contains 64 leds 2048 bits
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



def updateColumn(layer, xCord, yCord):
    """ view on top of matrix. Each 2x2 matrix will map one sound frequency range

                        00 01
                        10 00

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

    layer.updateLed(Led(), pos_00)
    layer.updateLed(Led(), pos_01)
    layer.updateLed(Led(), pos_10)
    layer.updateLed(Led(), pos_11)


