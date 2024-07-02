import numpy as np
from fir_coeffs import generate_fir_coeffs
from beamform import beamform_audio, beamform_for_angle

# Example usage
R, C = 4, 4
FOV_degrees = 90
num_taps = 100
audio_data = np.random.randn(1000, R * C)  # Simulated audio data

# Generate FIR coefficients
coeffs = generate_fir_coeffs(R, C, FOV_degrees, num_taps)

# Beamform the audio data
beamformed_audio = beamform_audio(audio_data, coeffs)

# Generate and apply FIR coefficients for a specific angle
angle_degrees = 45
beamformed_audio_for_angle = beamform_for_angle(audio_data, R, C, angle_degrees, num_taps)
