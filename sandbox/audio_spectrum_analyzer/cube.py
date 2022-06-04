import math


class Led:
    def __init__(self, vector):
        self.vector = vector
        self.color = self.vector.color.value
        self.pos = self.vector.axis.value

        # one led 16 bits
        if len(self.color) == 3:
            r, g, b = map(int, self.color)
            self.red = format(min([r, 15]), '04b')
            self.green = format(min([g, 15]), '04b')
            self.blue = format(min([b, 15]), '04b')
        else:
            self.red = format(0, '04b')
            self.green = format(0, '04b')
            self.blue = format(0, '04b')

    def translate_binary(self):
        return f"{self.red}{self.green}{self.blue}"

    def change_color(self, color):
        self.vector.color = color

    def get_led_position(self):
        return self.pos


class Layer:
    def __init__(self, leds):
        self.leds = leds
        # self.leds = [Led() for _ in range(64)]

    def update_led(self, led, position):
        self.leds[position] = led

    def translate_binary(self):
        layers_binary = None
        for led in self.leds:
            layers_binary += led.translate_binary()
        return layers_binary


class Frame:
    def __init__(self):
        self.layers = [Layer() for _ in range(8)]

    def get_layer(self, level):
        return self.layers[level]

    def add_layer(self, layer, level):
        self.layers[level] = layer

    def set_frame(self, frame):
        self.layers = frame

    def translate_binary(self):
        frames_binary = None
        for layer in self.layers:
            frames_binary += layer.translate_binary()
        return frames_binary

    def update_column(self, level, x_cord, y_cord, turn_on):
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
        pos_00 = 0 + x_cord * 2 + (y_cord * 16)
        pos_01 = 1 + x_cord * 2 + (y_cord * 16)
        pos_10 = 8 + x_cord * 2 + (y_cord * 16)
        pos_11 = 9 + x_cord * 2 + (y_cord * 16)

        if turn_on:
            brightness = 15
        else:
            brightness = 0

        # this should be modified to contain color values
        self.layers[level].update_led(Led(brightness, brightness, brightness), pos_00)
        self.layers[level].update_led(Led(brightness, brightness, brightness), pos_01)
        self.layers[level].update_led(Led(brightness, brightness, brightness), pos_10)
        self.layers[level].update_led(Led(brightness, brightness, brightness), pos_11)


class Animation:
    def __init__(self):
        self.frames = []

    def add_frame(self, frame):
        self.frames.append(frame)

    def translate_binary(self):
        animation_binary = None
        for frame in self.frames:
            animation_binary = frame.translate_binary()
        return animation_binary


def frequency_to_matrix(frequency):
    frequency_map = {0: {0, 0}, 1: {0, 1}, 2: {0, 2}, 3: {0, 3}, 4: {1, 0}, 5: {1, 1}, 6: {1, 2}, 7: {1, 3}, 8: {2, 0},
                     9: {2, 1}, 10: {2, 2}, 11: {2, 3}, 12: {2, 3}, 13: {3, 0}, 14: {3, 1}, 15: {3, 2}, 16: {3, 3}}
    matrix_number = math.floor(min(frequency / 625, 16))
    return frequency_map[matrix_number]


def spectrum_visualize(frame, frequency, power):
    x_cord, y_cord = frequency_to_matrix(frequency)
    for level in range(8):
        frame.update_column(level, x_cord, y_cord, level <= power)
