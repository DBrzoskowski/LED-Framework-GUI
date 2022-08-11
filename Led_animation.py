"""
LED Animation GUI "POC"
based on: https://www.glowscript.org/?fbclid=IwAR1HehsTnNPwcjGUmIz0-uG1XZuka_SypQoGb5I7NjspXkRWqmb5XsHbFEc#/user/GlowScriptDemos/folder/Examples/program/AtomicSolid-VPython

Installation:
    pip install vpython
"""
import time
import json
import txaio
import math
from random import uniform
from colormap import hex2rgb
from vpython import canvas, scene, vector, sphere, vec, color, curve, sleep, distant_light, button, rate
import asyncio
# scene.background = vector(0.95, 1, 1) # white background
txaio.use_asyncio()  # resolve problem with library https://stackoverflow.com/questions/34157314/autobahn-websocket-issue-while-running-with-twistd-using-tac-file

ANIMATION_FILE = 'animation_path.txt'


def fps_to_milliseconds(fps):
    return 1.0/fps


class Cube3D(canvas):
    def __init__(self, size, led_radius, spacing, momentumRange, **args):
        super().__init__(**args)
        self.leds = []
        self.center = 0.5 * (8 - 1) * vector(1, 1, 1)  # camera start view
        self.caption = """A model of a solid represented as leds connected by interledic bonds.

        To rotate "camera", drag with right button or Ctrl-drag.
        To zoom, drag with middle button or Alt/Option depressed, or use scroll wheel.
          On a two-button mouse, middle is left + right.
        To pan left/right and up/down, Shift-drag.
        Touch screen: pinch/extend to zoom, swipe or two-finger rotate."""
        self.lights = []
        self.old_led_color = {}

        # The part responsible for drawing
        self.drawing_path = {}
        self.drawing_path.setdefault('pos', [])
        self.drawing_path.setdefault('color', [])
        self.drawing_path.setdefault('fps', 30)
        self.drawing_color = None
        self.drawing_fps = None
        self.drawing_button_status = False
        self.animation_frame = []
        self.animation_step = []
        self.button_drawing = button(text="Not drawing", pos=self.title_anchor, bind=self.drawing_status)

        distant_light(direction=vector(0.22,  0.44,  0.88), color=color.gray(0.8))
        distant_light(direction=vector(-0.88, -0.22, -0.44), color=color.gray(0.3))
        distant_light(direction=vector(65.22,  65.44,  65.88), color=color.gray(0.8))
        distant_light(direction=vector(-65.88, -65.22, -65.44), color=color.gray(0.3))

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

    @staticmethod
    def hex2vector(drawing_color):
        try:
            if isinstance(drawing_color, str) and drawing_color.startswith('#'):
                r, g, b = hex2rgb(drawing_color)
                r, g, b = r / 255, g / 255, b / 255
                return vector(r, g, b)
        except TypeError as err:
            print(f"Wrong type {err}")

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
        if self.drawing_color and self.drawing_fps:
            col = self.drawing_color
            fps = self.drawing_fps

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

    def outline_inside_ankle_animation(self, col=vector(1, 0, 0), fps=30):
        if self.drawing_color and self.drawing_fps:
            col = self.drawing_color
            fps = self.drawing_fps

        for y in range(2, 6):
            get_all = [self.get_led_from_visible((2, y, i)) for i in range(2, 6)]
            for i in get_all:
                i.color = col
            rate(fps)

        for y in range(2, 6):
            get_all = [self.get_led_from_visible((y, 5, i)) for i in range(2, 6)]
            for i in get_all:
                i.color = col
            rate(fps)

        for y in reversed(range(2, 6)):
            get_all = [self.get_led_from_visible((5, y, i)) for i in range(2, 6)]
            for i in get_all:
                i.color = col
            rate(fps)

        for y in reversed(range(2, 6)):
            get_all = [self.get_led_from_visible((y, 2, i)) for i in range(2, 6)]
            for i in get_all:
                i.color = col
            rate(fps)

    def double_outline_animation(self, col=vector(1, 0, 0), fps=30):
        if self.drawing_color and self.drawing_fps:
            col = self.drawing_color
            fps = self.drawing_fps

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
            get_all_2 = [self.get_led_from_visible((y, 5, i)) for i in range(2, 6) if y in [3, 4, 5]]
            for i in get_all_1:
                i.color = vector(1, 1, 1)

            for i in get_all_2:
                i.color = col

            rate(fps)

        for y in reversed(range(0, 8)):
            get_all_1 = [self.get_led_from_visible((7, y, i)) for i in range(0, 8)]
            get_all_2 = [self.get_led_from_visible((5, y, i)) for i in range(2, 6) if y in [3, 4, 5]]
            for i in get_all_1:
                i.color = vector(1, 1, 1)

            for i in get_all_2:
                i.color = col

            rate(fps)

        for y in reversed(range(0, 8)):
            get_all_1 = [self.get_led_from_visible((y, 0, i)) for i in range(0, 8)]
            get_all_2 = [self.get_led_from_visible((y, 2, i)) for i in range(2, 6) if y in [3, 4, 5]]
            for i in get_all_1:
                i.color = vector(1, 1, 1)

            for i in get_all_2:
                i.color = col

            rate(fps)

    def save_animation_to_frame(self, file_path=ANIMATION_FILE, to_file=False):
        if self.drawing_path['pos'] and self.drawing_path['color']:
            return self.drawing_path

    def load_animation_from_file(self, file_path=ANIMATION_FILE):
        with open(file_path, 'r') as f:
            for i in f.readlines():
                line = json.loads(i)

                if line.get('color'):
                    colors = line.get('color')

                if line.get('pos'):
                    for pos in line.get('pos'):
                        # this must be reverse because we start drawing from the z axis
                        # e.g | x, y, z -> (6.0, 0.0, 7.0) | ==> | x, y, z -> (7.0, 0.0, 6.0) |
                        pos.reverse()
                        self.animation_step.append(self.get_led_from_visible(tuple(pos)))

                if line.get('fps'):
                    fps = line.get('fps')

                # animation process
                for led, col in zip(self.animation_step, colors):
                    r, g, b = col
                    led.color = vector(r, g, b)

                # clear animation step list
                self.animation_step = []

                # fps after chunk of animation end and waiting for next part
                rate(fps)
        # it's sleep because rate working based on windows time
        # (resolve problem with unexpected speed-up animation)
        sleep(fps_to_milliseconds(fps))

    def gui_args_builder(self, drawing_color, fps):
        self.drawing_color = drawing_color
        self.drawing_fps = fps
        try:
            if self.drawing_color and self.drawing_fps:
                return self.drawing_color, self.drawing_fps
        except ReferenceError as err:
            print(f"One of the arguments hasn't been defined -> {err}")

    def drawing(self, drawing_color=color.red, default_color=color.black, fps=30):
        # Get info from GUI about color and fps
        if self.drawing_color and self.drawing_fps:
            drawing_color = self.drawing_color
            fps = self.drawing_fps

        self.waitfor('click')
        hit = self.mouse.pick
        self.drawing_path['fps'] = fps

        drawing_color = self.hex2vector(drawing_color)

        if hit:
            if hit.color != drawing_color:
                self.old_led_color[hit.idx] = default_color

            hit.color = drawing_color if hit.color == self.old_led_color[hit.idx] else self.old_led_color[hit.idx]

            self.drawing_path['pos'].append(hit.pos.value)
            self.drawing_path['color'].append(hit.color.value)

    # def change_drawing_status_from_gui(self, value):
    #     self.drawing_button_status = value
    #     if value:
    #         self.button_drawing.delete()
    #         self.button_drawing = button(text="Drawing", pos=self.title_anchor, bind=self.drawing_status)
    #     else:
    #         self.button_drawing.delete()
    #         self.button_drawing = button(text="Not drawing", pos=self.title_anchor, bind=self.drawing_status)

    # button
    def drawing_status(self, b):
        self.drawing_button_status = not self.drawing_button_status
        if self.drawing_button_status:
            b.text = "Drawing"
            while self.drawing_button_status:
                self.drawing()
        else:
            b.text = "Not drawing"

    # def run_drawing(self):
    #     if not self.drawing_button_status:
    #         self.double_outline_animation(col=vector(1, 0, 0), fps=10)
    #
    #         # clear whole cube after test finish
    #         for i in self.get_visible_leds():
    #             i.color = vector(0, 0, 0)
    #         sleep(0.2)
    #     else:
    #         if self.drawing_button_status:
    #             self.drawing()


from menu_gui.menu import start_menu, AppWindow
from threading import Thread
from multiprocessing import Process

if __name__ == '__main__':
    c = Cube3D(8, 0.15 * 1, 1, 0.1 * 1 * math.sqrt(1 / 1))
    c.background = color.black  # temporarily to see the leds better
    # d1 = Thread(target=c.run_drawing())
    # d1.daemon = True
    # d1.start()
    t1 = Thread(target=start_menu(c))
    # t1.daemon = True
    t1.start()
