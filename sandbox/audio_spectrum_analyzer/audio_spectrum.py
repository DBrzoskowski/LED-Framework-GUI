import socket
import time
import pyaudio
import numpy as np
import matplotlib as mpl
import serial
from cube import *

mpl.use('TkAgg')  # or can use 'TkAgg', whatever you have/prefer

RATE = 44100
BUFFER = 882
PRINT_BLUE_LINE = True
PRINT_SPECTRUM_LINE = True

# Tuning values
STARTING_VALUE = 0
SAMPLE = 12  # Higher - lower number of spectrum's, 1 sample = 50Hz
FADE_SPEED = 0.4  # Higher - faster fading
CUBE_SECTORS = 16

SAMPLE_MAX = 0

p = pyaudio.PyAudio()
SPEAKERS = p.get_default_output_device_info()["hostApi"]


class SpectrumVisualizer:
    def __init__(self):
        self.frame = Frame()
        self.isActive = False
        self.frequencyMap = {0: (0, 0), 1: (0, 1), 2: (0, 2), 3: (0, 3), 4: (1, 0), 5: (1, 1), 6: (1, 2), 7: (1, 3),
                             8: (2, 0),
                             9: (2, 1), 10: (2, 2), 11: (2, 3), 12: (3, 0), 13: (3, 1), 14: (3, 2), 15: (3, 3)}
        self.stream = None
        self.recordedSamples = None
        self.maxSectorsValue = [0 for i in range(28)]
        self.rfft = None
        #self.serialcomm = serial.Serial('COM7', 9600)
        #self.serialcomm.timeout = 1


    def visualise(self, spectrumList):
        for index, value in enumerate(spectrumList):
            if index > 15:
                break
            power = value / 8 if value < 64 else 8
            self.updateSector(index, power)

    def updateSector(self, frequency, power):
        xCord, yCord = self.frequencyMap[frequency]
        for level in range(8):
            self.frame.updateColumn(level, xCord, yCord, level <= power)

    def startVisualisation(self):
        self.isActive = True
        self.stream = p.open(
            input_device_index=0,
            format=pyaudio.paFloat32,
            channels=1,
            rate=RATE,
            input=True,
            frames_per_buffer=BUFFER)
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
                b = np.fromstring(self.stream.read(BUFFER), dtype=np.float32)
                print()
                self.rfft = np.fft.rfft(b) * -10000
            except Exception as e:
                print('Failed, reason: ' + str(e))

            test = self.rfft[::]

            for i, point in enumerate(test):
                # get SAMPLE_AVERAGE of first (STARTING_VALUE)..(SAMPLE) elements
                if i % SAMPLE == 0:
                    SAMPLE_MAX = 0
                    sample_points = test[STARTING_VALUE:min((STARTING_VALUE + SAMPLE), len(test) - 1)]
                    for v in sample_points:
                        if v > SAMPLE_MAX:
                            SAMPLE_MAX = v

                    # replace SAMPLE_AVERAGE value for (STARTING_VALUE)..(SAMPLE) elements
                    for index in range(STARTING_VALUE, min(STARTING_VALUE + SAMPLE, len(test) - 1)):
                        test[index] = SAMPLE_MAX

                    STARTING_VALUE += SAMPLE
                    if STARTING_VALUE >= len(test):
                        STARTING_VALUE = 0

            test = np.maximum(test[::CUBE_SECTORS].real, self.maxSectorsValue)

            self.fadeCount(test)
            self.visualise(test)
#            self.serialSend()
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

        self.maxSectorsValue = test.round()

    def serialSend(self):
        print(self.frame.translateBinary())
        #self.serialcomm.write(self.frame)


    def wirelessSend(self):
        test = int(self.frame.translateBinary()[:2040], 2).to_bytes((len(self.frame.translateBinary()[:2040]) + 7) // 8, byteorder='big')
        red = bytes(test)

        #red = bytes([0xFF] * 255)
        green = bytes(self.frame.translateBinary()[255:511], 'utf-8')
        blue = bytes(self.frame.translateBinary()[511:767], 'utf-8')
        UDP_IP = "192.168.0.10"
        UDP_PORT = 4210
        print("UDP target IP:", UDP_IP)
        print("UDP target port:", UDP_PORT)
        print("Red:", red)

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # UDP
        sock.sendto(red, (UDP_IP, UDP_PORT))
        time.sleep(3)
#        print("Green:", green)
#        sock.sendto(green, (UDP_IP, UDP_PORT))
#        time.sleep(1)
 #       print("Blue:", blue)
  #      sock.sendto(blue, (UDP_IP, UDP_PORT))


visualiser = SpectrumVisualizer()
visualiser.startVisualisation()
