"""
LED Animation GUI "POC"
based on: https://www.glowscript.org/?fbclid=IwAR1HehsTnNPwcjGUmIz0-uG1XZuka_SypQoGb5I7NjspXkRWqmb5XsHbFEc#/user/GlowScriptDemos/folder/Examples/program/AtomicSolid-VPython

Installation:
    pip install -r requirements.txt
"""

import txaio
from random import uniform
from colormap import hex2rgb, rgb2hsv
from vpython import canvas, scene, vector, sqrt, sphere, vec, color, curve, sleep, distant_light, rate
from sandbox.audio_spectrum_analyzer.cube import Led, Layer, Frame, Animation

txaio.use_asyncio()  # resolve problem with library https://stackoverflow.com/questions/34157314/autobahn-websocket-issue-while-running-with-twistd-using-tac-file
scene.background = color.white  # scene color
N = 8  # N by N by N array of leds
k = 1
m = 1
spacing = 1
led_radius = 0.15 * spacing


class Cube3D(canvas):
    def __init__(self, size, led_radius, spacing, momentumRange, **args):
        super().__init__(**args)
        self.leds = []
        self.center = 0.5 * (N - 1) * vector(1, 1, 1)  # camera start view
        self.caption = """A model of a solid represented as leds connected by interledic bonds.

        To rotate "camera", drag with right button or Ctrl-drag.
        To zoom, drag with middle button or Alt/Option depressed, or use scroll wheel.
          On a two-button mouse, middle is left + right.
        To pan left/right and up/down, Shift-drag.
        Touch screen: pinch/extend to zoom, swipe or two-finger rotate."""
        self.lights = []
        self.old_led_color = {}

        self.default_state_list = []
        self.led_objects = []  # this is a Led() obj list

        # add some light to walls
        distant_light(direction=vector(0.22,  0.44,  0.88), color=color.gray(0.8))
        distant_light(direction=vector(-0.88, -0.22, -0.44), color=color.gray(0.3))
        distant_light(direction=vector(65.22,  65.44,  65.88), color=color.gray(0.8))
        distant_light(direction=vector(-65.88, -65.22, -65.44), color=color.gray(0.3))
        # distant_light(direction=vector(2.9, 2.8, 3.5), color=color.gray(0.3))
        # distant_light(direction=vector(-2.9, -2.8, -3.5), color=color.gray(0.8))
        # distant_light(direction=vector(1.6, 1.6, 2), color=color.gray(0.3))
        # distant_light(direction=vector(-1.6, -1.6, -2), color=color.gray(0.8))

        for z in range(0, size, 1):
            for x in range(0, size, 1):
                for y in range(0, size, 1):
                    led = sphere()
                    led.pos = vector(z, y, x) * spacing
                    led.radius = led_radius
                    if 0 <= x < size and 0 <= y < size and 0 <= z < size:
                        p = vec.random()
                        led.momentum = momentumRange * p
                        led.color = color.black
                    else:
                        # led.visible = False
                        led.momentum = vec(0, 0, 0)
                    led.index = len(self.leds)
                    self.leds.append(led)

    def get_visible_leds(self):
        return [i for i in self.leds if i.visible is True]

    def make_line(self, start, end):
        test_list = [vector(start.pos), vector(end.pos)]
        return curve(pos=test_list)

    def change_color(self, v):
        leds = self.get_visible_leds()
        if isinstance(v, str):
            color_picker = {
                'black': vector(0, 0, 0),
                'white': vector(1, 1, 1),
                'red': vector(1, 0, 0),
                'green': vector(0, 1, 0),
                'blue': vector(0, 0, 1),
                'yellow': vector(1, 1, 0),
                'cyan': vector(0, 1, 1),
                'magenta': vector(1, 0, 1),
                'orange': vector(1, 0.6, 0),
                'purple': vector(0.4, 0.2, 0.6)
            }
            cp = color_picker[v]
        elif type(v) == vector:
            cp = v
        else:
            print('change_color ERROR')
            cp = None

        for i in leds:
            i.color = cp

    def default_state(self):
        if not self.default_state_list:
            for visiable_led in self.get_visible_leds():
                led = Led(visiable_led)
                self.default_state_list.append(led)
        else:
            return self.default_state_list

    def get_led_from_visible(self, position):
        return [i for i in self.leds if (i.pos.z, i.pos.y, i.pos.x) == position][0]

    def reset_cube_state(self):
        for led in self.leds:
            led.color = vector(0, 0, 0)
        sleep(0.5)

    def random_color_animation(self):
        leds = self.get_visible_leds()  # 512 visible LEDs
        for i in leds:
            i.color = vector(uniform(0, 1), uniform(0, 1), uniform(0, 1))

    def outer_layer_animation(self, col=vector(1, 1, 1), fps=30):
        for y in range(0, 8):
            get_all = [self.get_led_from_visible((0, y, i)) for i in range(0, 8)]
            for i in get_all:
                i.color = col
            rate(fps)

        for y in range(0, 8):
            get_all = [self.get_led_from_visible((y, 7, i)) for i in range(0, 8)]
            for i in get_all:
                i.color = col
            rate(fps)

        for y in reversed(range(0, 8)):
            get_all = [self.get_led_from_visible((7, y, i)) for i in range(0, 8)]
            for i in get_all:
                i.color = col
            rate(fps)

        for y in reversed(range(0, 8)):
            get_all = [self.get_led_from_visible((y, 0, i)) for i in range(0, 8)]
            for i in get_all:
                i.color = col
            rate(fps)

    def outline_inside_ankle_animation(self, col, fps=30):
        for y in range(2, 6):
            get_all = [self.get_led_from_visible((2, y, i)) for i in range(2, 6)]
            for i in get_all:
                i.color = col
            rate(fps)

        for y in range(2, 6):
            get_all = [self.get_led_from_visible((y, 6, i)) for i in range(2, 6)]
            for i in get_all:
                i.color = col
            rate(fps)

        for y in reversed(range(2, 6)):
            get_all = [self.get_led_from_visible((6, y, i)) for i in range(2, 6)]
            for i in get_all:
                i.color = col
            rate(fps)

        for y in reversed(range(2, 6)):
            get_all = [self.get_led_from_visible((y, 2, i)) for i in range(2, 6)]
            for i in get_all:
                i.color = col
            rate(fps)

    def double_outline_animation(self, col, fps=30):
        for y in range(0, 8):
            get_all_1 = [self.get_led_from_visible((0, y, i)) for i in range(0, 8)]
            get_all_2 = [self.get_led_from_visible((2, y, i)) for i in range(2, 6) if y in [2, 3, 4, 5]]

            for i in get_all_1:
                i.color = vector(1, 1, 1)

            for i in get_all_2:
                i.color = col

            rate(fps)

        for y in range(0, 8):
            get_all_1 = [self.get_led_from_visible((y, 7, i)) for i in range(0, 8)]
            get_all_2 = [self.get_led_from_visible((y, 5, i)) for i in range(2, 6) if y in [3, 4, 5, 6]]

            for i in get_all_1:
                i.color = vector(1, 1, 1)

            for i in get_all_2:
                i.color = col

            rate(fps)

        for y in reversed(range(0, 8)):
            get_all_1 = [self.get_led_from_visible((7, y, i)) for i in range(0, 8)]
            get_all_2 = [self.get_led_from_visible((6, y, i)) for i in range(2, 6) if y in [3, 4, 5]]

            for i in get_all_1:
                i.color = vector(1, 1, 1)

            for i in get_all_2:
                i.color = col

            rate(fps)

        for y in reversed(range(0, 8)):
            get_all_1 = [self.get_led_from_visible((y, 0, i)) for i in range(0, 8)] 
            get_all_2 = [self.get_led_from_visible((y, 2, i)) for i in range(2, 6) if y in [3, 4, 5, 6]]

            for i in get_all_1:
                i.color = vector(1, 1, 1)

            for i in get_all_2:
                i.color = col

            rate(fps)

    def drawing(self, drawing_color=color.red, default_color=color.black):
        self.waitfor('click')
        hit = self.mouse.pick

        if isinstance(drawing_color, str) and drawing_color.startswith('#'):
            r, g, b = hex2rgb(drawing_color)
            r, g, b = rgb2hsv(r, g, b, False)
            drawing_color = vector(r, g, b)

        if hit:
            if hit.color != drawing_color:
                self.old_led_color[hit.idx] = default_color
                # led_obj = Led(drawing_color.value)
                # print(f'Translate binary -> {led_obj.translate_binary()}')

            hit.color = drawing_color if hit.color == self.old_led_color[hit.idx] else self.old_led_color[hit.idx]


c = Cube3D(N, led_radius, spacing, 0.1 * spacing * sqrt(k / m))
c.background = color.black  # temporarily to see the LEDs better
# time.sleep(2)
# c.double_outline_animation(color=vector(1, 0, 0))
# While it's unnecessary
while True:
    drawing = False

    if not drawing:
        c.default_state()
        c.outer_layer_animation()
        c.reset_cube_state()
    else:
        c.drawing(drawing_color='#aa55ff')
