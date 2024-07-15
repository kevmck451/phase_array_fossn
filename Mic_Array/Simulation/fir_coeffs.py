
from scipy.signal import firwin
import numpy as np


FOV_degrees = 90
num_taps = 100


def generate_fir_coeffs_for_array(R, C, R_out, C_out):
    angle_rad = np.deg2rad(FOV_degrees / 2) if FOV_degrees != 0 else np.deg2rad(0.1)
    return generate_coeffs(R, C, R_out, C_out, angle_rad)


def generate_fir_coeffs_for_angle(R, C, R_out, C_out, angle_degrees):
    angle_rad = np.deg2rad(angle_degrees) if angle_degrees != 0 else np.deg2rad(0.1)
    return generate_coeffs(R, C, R_out, C_out, angle_rad)


def generate_coeffs(R, C, R_out, C_out, angle_rad):
    delay_max = (R * C - 1) / (2 * np.pi * angle_rad) if angle_rad != 0 else 1

    coeffs = []
    for r in range(R_out):
        row_coeffs = []
        for c in range(C_out):
            delay = (r * C_out + c) * delay_max / (R_out * C_out)
            fir_coeff = firwin(num_taps, cutoff=0.5, window='hamming', pass_zero=True)
            row_coeffs.append(fir_coeff * delay)
        coeffs.append(row_coeffs)

    return np.array(coeffs)
