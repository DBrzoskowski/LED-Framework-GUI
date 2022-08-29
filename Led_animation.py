"""
LED Animation GUI "POC"
based on: https://www.glowscript.org/?fbclid=IwAR1HehsTnNPwcjGUmIz0-uG1XZuka_SypQoGb5I7NjspXkRWqmb5XsHbFEc#/user/GlowScriptDemos/folder/Examples/program/AtomicSolid-VPython

Installation:
    pip install vpython
"""

import sys
import os

sys.path.append(os.getcwd())

import json
import txaio
import copy
from colormap import hex2rgb
from vpython import canvas, sphere, vec, color, sleep, distant_light, rate
from menu_gui.menu import DoStartGUI
from sandbox.audio_spectrum_analyzer.LedManager import *
txaio.use_asyncio()  # resolve problem with library https://stackoverflow.com/questions/34157314/autobahn-websocket-issue-while-running-with-twistd-using-tac-file

ANIMATION_FILE = 'animation_path.txt'

drawing_path = []


def fps_to_milliseconds(fps):
    return 1.0/fps


class Cube3D(canvas):

    def __init__(self, size, led_radius, spacing, momentum_range):
        self._size = size
        self._led_radius = led_radius
        self._spacing = spacing
        self._momentum_range = momentum_range

    def initialize(self):
        """
        This method it's necessary to re-init the right one simulation inside GUI
        """
        super().__init__()
        self.leds = []
        self.center = 0.5 * (8 - 1) * vector(1, 1, 1)  # camera start view

        self.send_to_cube_flag = False

        self.height = 500
        self.width = 650

        self.lights = []
        self.old_led_color = {}

        self.abort_animation_thread = True
        self.animation_thread = None

        # The part responsible for drawing
        self.drawing_path = {}
        self.drawing_path.setdefault("pos", [])
        self.drawing_path.setdefault("color", [])
        self.drawing_path.setdefault("fps", 30)
        self.drawing_color = None
        self.drawing_fps = 30
        self.animation_step = []
        self.drawing_path_list = []

        self.background = vector(0.12, 0.12, 0.06)

        distant_light(direction=vector(0.22, 0.44, 0.88), color=color.gray(0.8))
        distant_light(direction=vector(-0.88, -0.22, -0.44), color=color.gray(0.3))
        distant_light(direction=vector(65.22, 65.44, 65.88), color=color.gray(0.8))
        distant_light(direction=vector(-65.88, -65.22, -65.44), color=color.gray(0.3))

        for z in range(0, self._size, 1):
            for x in range(0, self._size, 1):
                for y in range(0, self._size, 1):
                    led = sphere()
                    led.pos = vector(x, y, z) * self._spacing
                    led.radius = self._led_radius
                    if 0 <= x < self._size and 0 <= y < self._size and 0 <= z < self._size:
                        p = vec.random()
                        led.momentum = self._momentum_range * p
                        led.color = color.black
                    else:
                        led.momentum = vec(0, 0, 0)
                    led.index = len(self.leds)
                    self.leds.append(led)

    def binding(self):
        self.bind('click', self.led_on_click_event)  # Bind LED on click event

    def unbinding(self):
        self.unbind('click', self.led_on_click_event)  # Disabled LEDs on click event

    def update_simulated_cube(self, frame):
        for z in range(0, 8):
            for y in range(0, 8):
                for x in range(0, 8):
                    r, g, b = frame.getLedColor(x, y, z)
                    color = vector(r * 0.0625, g * 0.0625, b * 0.0625)
                    led_index = x + (y * 8) + (z * 64)

                    self.leds[led_index].color = color

    def led_on_click_event(self, ev):
        hit = self.mouse.pick
        self.drawing_path["fps"] = self.drawing_fps

        drawing_color = self.hex2vector(self.drawing_color)

        if hit:
            if hit.color != drawing_color:
                self.old_led_color[hit.idx] = drawing_color

            hit.color = drawing_color if hit.color == self.old_led_color[hit.idx] else self.old_led_color[hit.idx]

            self.drawing_path["pos"].append(hit.pos.value)
            self.drawing_path["color"].append(hit.color.value)

    @staticmethod
    def hex2vector(drawing_color):
        try:
            if isinstance(drawing_color, str) and drawing_color.startswith('#'):
                r, g, b = hex2rgb(drawing_color)
                r, g, b = r / 255, g / 255, b / 255
                return vector(r, g, b)
        except TypeError as err:
            print(f"Wrong type {err}")

    def get_led_from_visible(self, position):
        return [i for i in self.leds if (i.pos.z, i.pos.y, i.pos.x) == position][0]

    def reset_cube_state(self):
        for led in self.leds:
            led.color = vector(0, 0, 0)
        sleep(0.5)

    def random_color_animation(self):
        for i in self.leds:
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

    def save_animation_frame_list(self):
        if self.drawing_path["pos"] and self.drawing_path["color"]:
            copy_dict = copy.deepcopy(self.drawing_path)
            self.drawing_path_list.append(copy_dict)
            self.drawing_path["pos"] = []
            self.drawing_path["color"] = []
        return self.drawing_path_list

    def load_animation_from_file(self, file_path=ANIMATION_FILE):
        with open(file_path, 'r') as f:
            for i in f.readlines():
                line = json.loads(i)

                if line.get("color"):
                    colors = line.get("color")

                if line.get("pos"):
                    for pos in line.get("pos"):
                        # this must be reverse because we start drawing from the z axis
                        # e.g | x, y, z -> (6.0, 0.0, 7.0) | ==> | x, y, z -> (7.0, 0.0, 6.0) |
                        pos.reverse()
                        self.animation_step.append(self.get_led_from_visible(tuple(pos)))

                if line.get("fps"):
                    fps = line.get("fps")

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

    def set_drawing_color(self, drawing_color):
        self.drawing_color = drawing_color

    def set_drawing_fps(self, fps):
        self.drawing_fps = fps


if __name__ == '__main__':
    # Just create memory for object and pass that to thread
    c = Cube3D(8, 0.15 * 1, 1, 0.1 * 1 * math.sqrt(1 / 1))

    # initialize GUI thread, which will start browser listener
    c.gui_thread = DoStartGUI(c)
    c.gui_thread.start()

    # fully initialize cube and open web socket with simulation
    c.initialize()

    # Wait for GUI thread to end
    c.gui_thread.join()
    print("Program ended")

