"""
LED Animation GUI "POC"
based on: https://www.glowscript.org/?fbclid=IwAR1HehsTnNPwcjGUmIz0-uG1XZuka_SypQoGb5I7NjspXkRWqmb5XsHbFEc#/user/GlowScriptDemos/folder/Examples/program/AtomicSolid-VPython

Installation:
    pip install vpython
"""
from random import uniform
from vpython import canvas, scene, vector, sqrt, sphere, vec, color, curve, sleep, distant_light


# scene.background = vector(0.95, 1, 1) # white background
scene.background = color.black  # scene color
N = 8  # N by N by N array of leds
k = 1
m = 1
spacing = 1
led_radius = 0.15 * spacing


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

        # TODO: WIP work on light for each wall
        distant_light(direction=vector(0.22,  0.44,  0.88), color=color.gray(0.8))
        distant_light(direction=vector(-0.88, -0.22, -0.44), color=color.gray(0.3))
        distant_light(direction=vector(65.22,  65.44,  65.88), color=color.gray(0.8))
        distant_light(direction=vector(-65.88, -65.22, -65.44), color=color.gray(0.3))

        # Create (N+2)^3 LED in a grid; the outermost LED is fixed and invisible
        for z in range(-1, size + 1, 1):
            for y in range(-1, size + 1, 1):
                for x in range(-1, size + 1, 1):
                    led = sphere()
                    led.pos = vector(x, y, z) * spacing
                    led.radius = led_radius
                    led.color = vector(0, 0.58, 0.69)
                    if 0 <= x < size and 0 <= y < size and 0 <= z < size:
                        p = vec.random()
                        led.momentum = momentumRange * p
                        led.color = color.black
                    else:
                        led.visible = False
                        led.momentum = vec(0, 0, 0)
                    led.index = len(self.leds)
                    self.leds.append(led)
        # Create lines between LED
        for led in self.leds:
            if led.visible:
                if led.pos.x == 0:
                    self.make_line(self.leds[led.index - 1], led)
                    self.make_line(led, self.leds[led.index + 1])
                elif led.pos.x == size - 1:
                    self.make_line(led, self.leds[led.index + 1])
                else:
                    self.make_line(led, self.leds[led.index + 1])

                if led.pos.y == 0:
                    self.make_line(self.leds[led.index - (size + 2)], led)
                    self.make_line(led, self.leds[led.index + (size + 2)])
                elif led.pos.y == size - 1:
                    self.make_line(led, self.leds[led.index + (size + 2)])
                else:
                    self.make_line(led, self.leds[led.index + (size + 2)])

                if led.pos.z == 0:
                    self.make_line(self.leds[led.index - (size + 2) ** 2], led)
                    self.make_line(led, self.leds[led.index + (size + 2) ** 2])
                elif led.pos.z == size - 1:
                    self.make_line(led, self.leds[led.index + (size + 2) ** 2])
                else:
                    self.make_line(led, self.leds[led.index + (size + 2) ** 2])

    # Create line between LEDs

    def visible_leds(self):
        return [i for i in self.leds if i.visible is True]

    def make_line(self, start, end):
        test_list = [vector(start.pos), vector(end.pos)]
        return curve(pos=test_list)

    def change_color(self, v):
        leds = self.visible_leds()
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

    def random_color(self):
        leds = self.visible_leds()  # 512 visible LEDs
        for i in leds:
            i.color = vector(uniform(0, 1), uniform(0, 1), uniform(0, 1))

    def layers_change(self):
        # WIP function
        leds = self.visible_leds()
        leds[0].color = color.orange
        leds[1].color = color.white
        # leds[2].color = color.red
        # leds[3].color = color.green
        # leds[4].color = color.blue
        # leds[5].color = color.yellow
        # leds[6].color = color.cyan
        # leds[7].color = color.magenta
        # leds[8].color = color.orange

        leds[503].color = color.blue
        leds[504].color = color.orange
        leds[505].color = color.red
        leds[506].color = color.green
        leds[511].color = color.yellow

        leds[448].color = color.yellow

# TODO This need to be re-writed
def click(evt):
    led_to_change = [i for i in c.leds if
                     int(i.pos.x) == int(evt.pos.x) and int(i.pos.y) == int(evt.pos.y) and int(i.pos.z) == int(
                         evt.pos.z)]
    led_to_change[0].color = color.red


c = Cube3D(N, led_radius, spacing, 0.1 * spacing * sqrt(k / m))

while True:
    sleep(fps_to_milliseconds(30))
    # c.layers_change()
    c.random_color()

