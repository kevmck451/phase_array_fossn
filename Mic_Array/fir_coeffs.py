import numpy as np
from scipy.signal import firwin


def generate_fir_coeffs(R, C, FOV_degrees, num_taps=100):
    M = R * C
    angle_rad = np.deg2rad(FOV_degrees)
    delay_max = (M - 1) / (2 * np.pi * angle_rad)

    # Generate coefficients
    coeffs = []
    for r in range(R):
        row_coeffs = []
        for c in range(C):
            delay = (r * C + c) * delay_max / M
            fir_coeff = firwin(num_taps, cutoff=0.5, window="hamming", pass_zero=True)
            row_coeffs.append(fir_coeff * delay)
        coeffs.append(row_coeffs)

    return np.array(coeffs)


def generate_fir_coeffs_for_angle(R, C, angle_degrees, num_taps=100):
    angle_rad = np.deg2rad(angle_degrees)
    delay_max = (R * C - 1) / (2 * np.pi * angle_rad)

    coeffs = []
    for r in range(R):
        row_coeffs = []
        for c in range(C):
            delay = (r * C + c) * delay_max / (R * C)
            fir_coeff = firwin(num_taps, cutoff=0.5, window="hamming", pass_zero=True)
            row_coeffs.append(fir_coeff * delay)
        coeffs.append(row_coeffs)

    return np.array(coeffs)
