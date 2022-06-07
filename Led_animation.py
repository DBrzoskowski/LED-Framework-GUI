"""
LED Animation GUI "POC"
based on: https://www.glowscript.org/?fbclid=IwAR1HehsTnNPwcjGUmIz0-uG1XZuka_SypQoGb5I7NjspXkRWqmb5XsHbFEc#/user/GlowScriptDemos/folder/Examples/program/AtomicSolid-VPython

Installation:
    pip install -r requirements.txt
"""
import os

import txaio
import json
from random import uniform
from colormap import hex2rgb, rgb2hsv
from vpython import canvas, scene, vector, sqrt, sphere, vec, color, curve, sleep, distant_light, rate, cos, sin
from sandbox.audio_spectrum_analyzer.cube import Led, Layer, Frame, Animation

txaio.use_asyncio()  # resolve problem with library https://stackoverflow.com/questions/34157314/autobahn-websocket-issue-while-running-with-twistd-using-tac-file
scene.background = color.white  # scene color
N = 8  # N by N by N array of leds
k = 1
m = 1
spacing = 1
led_radius = 0.15 * spacing

SIM_CUBE_FILE = 'sim_cube.txt'
REAL_CUBE_FILE = 'real_cube.txt'


def fps_to_milliseconds(fps):
    return 1.0/fps


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

        self.drawing_path = {}
        self.drawing_path.setdefault('pos', [])
        self.drawing_path.setdefault('color', [])
        self.drawing_path.setdefault('fps', 30)
        self.leds_from_file = []

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

        # Remove file after object init
        if os.path.exists(SIM_CUBE_FILE):
            os.remove(SIM_CUBE_FILE)

        for z in range(0, size, 1):
            for x in range(0, size, 1):
                for y in range(0, size, 1):
                    led = sphere(make_trail=True)
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

    def save_sim_animation(self):
        if self.drawing_path['pos'] and self.drawing_path['color']:
            with open(SIM_CUBE_FILE, 'a') as f:
                f.write(json.dumps(self.drawing_path) + '\n')

                # reset data after save
                self.drawing_path['pos'] = []
                self.drawing_path['color'] = []

    def save_real_animation(self):
        with open(REAL_CUBE_FILE, 'a') as f:
            binary_cube_state = ''.join([Led(i).translate_binary() for i in self.get_visible_leds()])
            f.writelines(binary_cube_state)

    def load_sim_animation_from_file(self, file_path=SIM_CUBE_FILE):
        with open('sim_cube_test.txt', 'r') as f:
            for i in f.readlines():
                line = json.loads(i)

                if line.get('color'):
                    colors = line.get('color')

                if line.get('pos'):
                    for pos in line.get('pos'):
                        # this must be reverse because we start drawing from the z axis
                        # e.g | x, y, z -> (6.0, 0.0, 7.0) | ==> | x, y, z -> (7.0, 0.0, 6.0) |
                        pos.reverse()
                        self.leds_from_file.append(self.get_led_from_visible(tuple(pos)))

                if line.get('fps'):
                    fps = line.get('fps')

                # animation process
                for led, col in zip(self.leds_from_file, colors):
                    r, g, b = col
                    led.color = vector(r, g, b)

                # clear animation step list
                self.leds_from_file = []

                # fps after chunk of animation end and waiting for next part
                rate(fps)

        # it's sleep because rate working based on windows time
        # (resolve problem with unexpected speed-up animation)
        sleep(fps_to_milliseconds(fps))

    def drawing(self, drawing_color=color.red, default_color=color.black, fps=30):
        self.waitfor('click')
        hit = self.mouse.pick
        self.drawing_path['fps'] = fps

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

            self.drawing_path['pos'].append(hit.pos.value)
            self.drawing_path['color'].append(hit.color.value)


# c = Cube3D(N, led_radius, spacing, 0.1 * spacing * sqrt(k / m))
# c.background = color.black  # temporarily to see the LEDs better
#
# ow = 5
# while True:
#     drawing = False
#
#     if not drawing:
#         # c.outer_layer_animation()
#         # c.load_sim_animation_from_file()
#         c.save_real_animation()
#         # it'
#         # sleep(fps_to_milliseconds(10))
#         # c.reset_cube_state()
#     else:
#         c.drawing(drawing_color='#aa55ff')
#         print(c.drawing_path)
#         # c.save_sim_animation()


