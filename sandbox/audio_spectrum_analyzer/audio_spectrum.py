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


class SpectrumVisualizer:
    def __init__(self):
        self.frame = LEDFrame()
        self.isActive = False
        self.duration = 120000
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

    def startVisualisation(self, duration=120000):
        self.isActive = True
        self.duration = duration
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

    def current_milli_time(self):
        return round(time.time() * 1000)

    def startSoundAnalysis(self):
        start = self.current_milli_time()

        while self.isActive:
            global SAMPLE_MAX
            global STARTING_VALUE
            global SAMPLE

            if (self.current_milli_time() - start) > self.duration:
                self.isActive = False
                return

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
            maxSamples = self.countFrequency()
            self.fadeCount(maxSamples)
            self.visualise(self.maxSectorsValue)
            # self.serialSend()
            self.wirelessSend()

    def countFrequency(self):
        maxSamples = []

        for i in range(4):
            maxSamples.append(np.maximum(max(self.rfft[i:i + 1].real * 10), self.maxSectorsValue[i]))

        maxSamples.append(np.maximum(max(self.rfft[4:6].real * 10), self.maxSectorsValue[4]))
        maxSamples.append(np.maximum(max(self.rfft[6:9].real * 10), self.maxSectorsValue[5]))
        maxSamples.append(np.maximum(max(self.rfft[9:12].real * 10), self.maxSectorsValue[6]))
        maxSamples.append(np.maximum(max(self.rfft[12:17].real * 10), self.maxSectorsValue[7]))
        maxSamples.append(np.maximum(max(self.rfft[17:25].real * 10), self.maxSectorsValue[8]))
        maxSamples.append(np.maximum(max(self.rfft[25:35].real * 10), self.maxSectorsValue[9]))
        maxSamples.append(np.maximum(max(self.rfft[35:50].real * 10), self.maxSectorsValue[10]))
        maxSamples.append(np.maximum(max(self.rfft[50:70].real * 10), self.maxSectorsValue[11]))
        maxSamples.append(np.maximum(max(self.rfft[70:100].real * 10), self.maxSectorsValue[12]))
        maxSamples.append(np.maximum(max(self.rfft[100:200].real * 10), self.maxSectorsValue[13]))
        maxSamples.append(np.maximum(max(self.rfft[200:400].real * 10), self.maxSectorsValue[14]))
        maxSamples.append(np.maximum(max(self.rfft[400:].real * 10), self.maxSectorsValue[15]))
        return maxSamples

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
        time.sleep(0.02)
        self.frame.clear()