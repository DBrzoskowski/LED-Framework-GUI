"""
LED Animation GUI "POC"
based on: https://www.glowscript.org/?fbclid=IwAR1HehsTnNPwcjGUmIz0-uG1XZuka_SypQoGb5I7NjspXkRWqmb5XsHbFEc#/user/GlowScriptDemos/folder/Examples/program/AtomicSolid-VPython
"""

from vpython import *

# Bruce Sherwood
scene.background = vector(0.95, 1, 1)
N = 8  # N by N by N array of leds
# Surrounding the N**3 leds is another layer of invisible fixed-position leds
# that provide stability to the lattice.
k = 1
m = 1
spacing = 1
led_radius = 0.15 * spacing
L0 = spacing - 1.8 * led_radius
V0 = (0.5 * led_radius)  # initial volume of spring

scene.center = 0.5 * (N - 1) * vector(1, 1, 1)
dt = 0.04 * (2 * pi * sqrt(m / k))
axes = [vector(1, 0, 0), vector(0, 1, 0), vector(0, 0, 1)]
scene.caption = """A model of a solid represented as leds connected by interledic bonds.

To rotate "camera", drag with right button or Ctrl-drag.
To zoom, drag with middle button or Alt/Option depressed, or use scroll wheel.
  On a two-button mouse, middle is left + right.
To pan left/right and up/down, Shift-drag.
Touch screen: pinch/extend to zoom, swipe or two-finger rotate."""


class Cube3D:
    def __init__(self, size, led_radius, spacing, momentumRange):
        self.leds = []

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
    def make_line(self, start, end):
        test_list = [vector(start.pos), vector(end.pos)]
        return curve(pos=test_list)


c = Cube3D(N, led_radius, spacing, 0.1 * spacing * sqrt(k / m))


#TODO This need to be re-writed
def click(evt):
    led_to_change = [i for i in c.leds if
                     int(i.pos.x) == int(evt.pos.x) and int(i.pos.y) == int(evt.pos.y) and int(i.pos.z) == int(
                         evt.pos.z)]
    led_to_change[0].color = color.red


while True:
    rate(60)
    scene.bind('click', click)
