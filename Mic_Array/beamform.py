
from fir_coeffs import generate_fir_coeffs_for_angle

from scipy.signal import convolve
import numpy as np


def beamform_audio(audio_data, fir_coeffs, R, C, R_out, C_out):
    num_taps = fir_coeffs.shape[-1]
    beamformed_audio = np.zeros((audio_data.shape[0], R_out * C_out))

    for r in range(R_out):
        for c in range(C_out):
            mic_index = (r % R) * C + (c % C)  # Wrap around indices for the input audio array
            mic_data = audio_data[:, mic_index]
            beamformed_audio[:, r * C_out + c] = convolve(mic_data, fir_coeffs[r, c], mode='same')

    return beamformed_audio


def beamform_for_angle(audio_data, R, C, R_out, C_out, angle_degrees):
    fir_coeffs = generate_fir_coeffs_for_angle(R, C, R_out, C_out, angle_degrees)
    return beamform_audio(audio_data, fir_coeffs, R, C, R_out, C_out)
