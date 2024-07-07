
from fir_coeffs import generate_fir_coeffs_for_array
from beamform import beamform_audio, beamform_for_angle

import numpy as np

R, C = 4, 4  # Original 4x4 microphone array
R_out, C_out = 5, 5  # Desired output 5x5 beamformed audio array

audio_data = np.random.rand(1000, R * C)  # Simulated audio data for 4x4 array

# Generate FIR coefficients for the desired output size
coeffs = generate_fir_coeffs_for_array(R, C, R_out, C_out)

# Beamform the audio data to the desired output size
beamformed_audio = beamform_audio(audio_data, coeffs, R, C, R_out, C_out)

# Generate and apply FIR coefficients for a specific angle and desired output size
angle_degrees = 45 # [-FOV/2 , FOV/2]
beamformed_audio_for_angle = beamform_for_angle(audio_data, R, C, R_out, C_out, angle_degrees)

