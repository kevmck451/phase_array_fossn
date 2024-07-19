import numpy as np
import struct

import struct


def binary(num):
    return ''.join('{:0>8b}'.format(c) for c in struct.pack('!f', num))


def float_to_fixed(x, e):
    x_float = x * (2 ** e)
    x_int = int(x_float)
    return x_int
    # print(x)
    # print(x_float)
    # print(x_int)
    # print('')


def fixed_to_float(x, e):
    return x / (2 ** e)