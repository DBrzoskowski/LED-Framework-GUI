import socket
import time

import pyaudio
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation
import matplotlib as mpl
import serial
from LedManager import *

mpl.use('TkAgg')  # or can use 'TkAgg', whatever you have/prefer

RATE = 44100
BUFFER = 882
PRINT_BLUE_LINE = True
PRINT_SPECTRUM_LINE = True

# Tuning values
STARTING_VALUE = 0
SAMPLE = 1  # Higher - lower number of spectrum's, 1 sample = 50Hz
FADE_SPEED = 2   # Higher - faster fading
CUBE_SECTORS = 16

SAMPLE_MAX = 0

p = pyaudio.PyAudio()
SPEAKERS = p.get_default_output_device_info()["hostApi"]
stream = p.open(
    input_device_index=2,  # Select proper input device index <---------------------------- [!!!!!!!!!!!!!!!!!!!!]
    format=pyaudio.paFloat32,
    channels=1,
    rate=RATE,
    input=True,
    frames_per_buffer=BUFFER,
)

fig = plt.figure()
line1 = plt.plot([], [])[0]
line2 = plt.plot([], [])[0]

r = range(0, int(RATE / 2 + 1), int(RATE / BUFFER))
l = len(r)


def sectorsValue(list):
    return list[1][::CUBE_SECTORS].real.round()


def init_line():
    line1.set_data(r, [-1000] * l)
    line2.set_data(r, [-1000] * l)
    return line1, line2


def update_line(i):
    global SAMPLE_MAX
    global STARTING_VALUE
    global SAMPLE

    try:
        # print("1st step")
        b = np.fromstring(stream.read(BUFFER), dtype=np.float32)
        print("2nd step")
        data = np.fft.rfft(b)
    except Exception as e:
        print('Failed, reason: ' + str(e))
        line1.set_data(r, [0])
        line2.set_data(r, [0])
        return line1, line2

    data = data * -1

    if PRINT_BLUE_LINE:
        line1.set_data(r, data)
    else:
        line1.set_data(r, [0])

    test = np.maximum(data, line2.get_data())

    for i, point in enumerate(test[1]):
        # get SAMPLE_AVERAGE of first (STARTING_VALUE)..(SAMPLE) elements
        if i % SAMPLE == 0:
            SAMPLE_MAX = 0
            sample_points = test[1][STARTING_VALUE:min((STARTING_VALUE + SAMPLE), len(test[1]) - 1)]
            for v in sample_points:
                if v > SAMPLE_MAX:
                    SAMPLE_MAX = v
                    # print('dd'+v)

            # replace SAMPLE_AVERAGE value for (STARTING_VALUE)..(SAMPLE) elements
            for index in range(STARTING_VALUE, min(STARTING_VALUE + SAMPLE, len(test[1]) - 1)):
                test[1][index] = SAMPLE_MAX

            STARTING_VALUE += SAMPLE
            if STARTING_VALUE >= len(test[1]):
                STARTING_VALUE = 0

    for index in range(0, len(test[1]) - 1):
        if test[1][index] >= FADE_SPEED:
            if test[1][index] >= 70:
                test[1][index] = test[1][index] - (FADE_SPEED * 16)
            elif test[1][index] >= 60:
                test[1][index] = test[1][index] - (FADE_SPEED * 12)
            elif test[1][index] >= 50:
                test[1][index] = test[1][index] - (FADE_SPEED * 8)
            elif test[1][index] >= 40:
                test[1][index] = test[1][index] - (FADE_SPEED * 6)
            elif test[1][index] >= 30:
                test[1][index] = test[1][index] - (FADE_SPEED * 4)
            elif test[1][index] >= 20:
                test[1][index] = test[1][index] - (FADE_SPEED * 2)
            else:
                test[1][index] = test[1][index] - FADE_SPEED
        else:
            test[1][index] = 0

    if PRINT_SPECTRUM_LINE:
        line2.set_data(test)

    return line1, line2

def CLIEqualiser(klatka):
    klatka = klatka[:2049]
    print("sector1: " + '#' * int(klatka[::64].count('1')/4))
    print("sector2: " + '#' * int(klatka[2::64].count('1')/4))
    print("sector3: " + '#' * int(klatka[4::64].count('1')/4))
    print("sector4: " + '#' * int(klatka[6::64].count('1')/4))
    print("sector5: " + '#' * int(klatka[16::64].count('1')/4))
    print("sector6: " + '#' * int(klatka[18::64].count('1')/4))
    print("sector7: " + '#' * int(klatka[20::64].count('1')/4))
    print("sector8: " + '#' * int(klatka[22::64].count('1')/4))
    print("sector9: " + '#' * int(klatka[32::64].count('1')/4))
    print("sector10: " + '#' * int(klatka[34::64].count('1')/4))
    print("sector11: " + '#' * int(klatka[36::64].count('1')/4))
    print("sector12: " + '#' * int(klatka[38::64].count('1')/4))
    print("sector13: " + '#' * int(klatka[48::64].count('1')/4))
    print("sector14: " + '#' * int(klatka[50::64].count('1')/4))
    print("sector15: " + '#' * int(klatka[52::64].count('1')/4))
    print("sector16: " + '#' * int(klatka[54::64].count('1')/4))




class SpectrumVisualizer:
    def __init__(self):
        self.frame = LEDFrame()
        self.isActive = False
        self.frequencyMap = {0: (0, 0), 1: (0, 1), 2: (0, 2), 3: (0, 3), 4: (1, 0), 5: (1, 1), 6: (1, 2), 7: (1, 3),
                             8: (2, 0),
                             9: (2, 1), 10: (2, 2), 11: (2, 3), 12: (3, 0), 13: (3, 1), 14: (3, 2), 15: (3, 3)}
        self.stream = None
        self.recordedSamples = None
        self.maxSectorsValue = [0 for i in range(28)]
        self.rfft = [0 for i in range(442)]


    def visualise(self, spectrumList):
        for index, value in enumerate(spectrumList):
            if index > 15:
                break
            level = int(value / 8) if value < 64 else 8
            self.updateSector(index, level)

    def updateSector(self, frequency, level):
        xCord, yCord = self.frequencyMap[frequency]
        self.frame.updateColumn(level, xCord, yCord)

    def startVisualisation(self):
        self.isActive = True
        """self.stream = p.open(
            input_device_index=2,
            format=pyaudio.paFloat32,
            channels=1,
            rate=RATE,
            input=True,
            frames_per_buffer=BUFFER)"""
        self.startSoundAnalysis()

    def stopVisualisation(self):
        self.isActive = False
        self.stream.close()

    def startSoundAnalysis(self):
        while self.isActive:
            global SAMPLE_MAX
            global STARTING_VALUE
            global SAMPLE

            try:
                b = np.fromstring(stream.read(BUFFER), dtype=np.float32)
                print()
                self.rfft = np.fft.rfft(b) * -1
            except Exception as e:
                print('Failed, reason: ' + str(e))

            for i, point in enumerate(self.rfft):
                # get SAMPLE_AVERAGE of first (STARTING_VALUE)..(SAMPLE) elements
                if i % SAMPLE == 0:
                    SAMPLE_MAX = 0
                    sample_points = self.rfft[STARTING_VALUE:min((STARTING_VALUE + SAMPLE), len(self.rfft) - 1)]
                    for v in sample_points:
                        if v > SAMPLE_MAX:
                            SAMPLE_MAX = v
                            # print('dd'+v)

                    # replace SAMPLE_AVERAGE value for (STARTING_VALUE)..(SAMPLE) elements
                    for index in range(STARTING_VALUE, min(STARTING_VALUE + SAMPLE, len(self.rfft) - 1)):
                        self.rfft[index] = SAMPLE_MAX

                    STARTING_VALUE += SAMPLE
                    if STARTING_VALUE >= len(self.rfft):
                        STARTING_VALUE = 0
            maxSamples = np.maximum(self.rfft[::CUBE_SECTORS].real * 10, self.maxSectorsValue)
            self.fadeCount(maxSamples)
            self.visualise(self.maxSectorsValue)
            #self.serialSend()
            self.wirelessSend()



    def fadeCount(self, test):
        for index in range(0, len(test) - 1):
            if test[index] >= FADE_SPEED:
                if test[index] >= 70:
                    test[index] = test[index] - (FADE_SPEED * 16)
                elif test[index] >= 60:
                    test[index] = test[index] - (FADE_SPEED * 12)
                elif test[index] >= 50:
                    test[index] = test[index] - (FADE_SPEED * 8)
                elif test[index] >= 40:
                    test[index] = test[index] - (FADE_SPEED * 6)
                elif test[index] >= 30:
                    test[index] = test[index] - (FADE_SPEED * 4)
                elif test[index] >= 20:
                    test[index] = test[index] - (FADE_SPEED * 2)
                else:
                    test[index] = test[index] - FADE_SPEED
            else:
                test[index] = 0

        self.maxSectorsValue = test



    def wirelessSend(self):
        sendFrame(self.frame)
        time.sleep(0.2)
        self.frame.clear()


plt.xlim([0, 10000])
plt.ylim(-10, 30)
plt.xlabel('Frequency [Hz]')
plt.ylabel('dB')
plt.title('Spectrometer')
plt.grid()

visualiser = SpectrumVisualizer()
visualiser.startVisualisation()

line_ani = matplotlib.animation.FuncAnimation(
    fig, update_line, init_func=init_line, interval=0, blit=True
)

plt.show()

"""
"""