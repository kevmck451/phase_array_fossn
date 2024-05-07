import numpy as np
import math
import matplotlib.pyplot as plt
from scipy.signal import convolve


def delay(x, y, z, theta, phi, sample_rate, filter_length, win_length):
    wx = math.cos(math.radians(phi)) * math.cos(math.radians(theta))
    wy = math.cos(math.radians(phi)) * math.sin(math.radians(theta))
    wz = math.sin(math.radians(phi))

    dt = ((wx * x) + (wy * y) + (wz * z)) / 343.3
    delay = (dt * sample_rate) - 0.5
    # print(str(wx) + " " + str(wy) + " " + str(wz))
    # print(str(dt) + " seconds")
    # print(str(delay) + " sample delay")

    tapWeight = np.zeros(filter_length)
    centerTap = win_length / 2
    for i in range(filter_length):
        # shifty shift
        x = i - delay

        # sinc = np.sin(math.pi * (x-centerTap)) / (math.pi * (x-centerTap));
        sinc = np.sinc(x - centerTap)

        # i don't usually like ham but here we are
        window = 0.54 - (0.46 * np.cos(2.0 * math.pi * (x + 0.5) / win_length))

        # tippity taps
        tapWeight[i] = window * sinc

    return tapWeight


def delayOnly(data, delay, filter_length, win_length):
    tapWeight = np.zeros(filter_length)
    centerTap = win_length / 2
    for i in range(filter_length):
        # shifty shift
        x = i - delay

        # sinc = np.sin(math.pi * (x-centerTap)) / (math.pi * (x-centerTap));
        sinc = np.sinc(x - centerTap)

        # i don't usually like ham but here we are
        window = 0.54 - (0.46 * np.cos(2.0 * math.pi * (x + 0.5) / win_length))

        # tippity taps
        tapWeight[i] = window * sinc

    return tapWeight



