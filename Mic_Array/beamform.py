from scipy.signal import convolve
import numpy as np


def beamform_audio(audio_data, fir_coeffs):
    R, C, num_taps = fir_coeffs.shape
    beamformed_audio = np.zeros(audio_data.shape[0] - num_taps + 1)

    for r in range(R):
        for c in range(C):
            beamformed_audio += convolve(audio_data[:, r * C + c], fir_coeffs[r, c], mode='valid')

    return beamformed_audio


def beamform_for_angle(audio_data, R, C, angle_degrees, num_taps=100):
    from fir_coeffs import generate_fir_coeffs_for_angle
    fir_coeffs = generate_fir_coeffs_for_angle(R, C, angle_degrees, num_taps)
    return beamform_audio(audio_data, fir_coeffs)
