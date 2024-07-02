

import numpy as np
import matplotlib.pyplot as plt

def array_factor(N, d, wavelength, angles):
    theta = np.deg2rad(angles)
    k = 2 * np.pi / wavelength
    beta = k * d * np.sin(theta)
    epsilon = 1e-10
    af = np.abs(np.sin(N * beta / 2) / (N * np.sin(beta / 2) + epsilon))
    return af

# Array specifications
N = 12  # Number of microphones
d = 0.08  # Spacing between microphones in meters
freq_lower = 100
freq_top = 4000
frequencies = np.arange(freq_lower, freq_top + 1, 10)
c = 343
angles = np.linspace(-90, 90, 360)
epsilon = 1e-10

beam_levels = np.zeros((len(frequencies), len(angles)))

for i, f in enumerate(frequencies):
    wavelength = c / f
    af = array_factor(N, d, wavelength, angles)
    af[af < epsilon] = epsilon
    beam_levels[i, :] = 20 * np.log10(af)

plt.figure(figsize=(14, 8))
pcm = plt.pcolormesh(angles, frequencies, beam_levels, shading='auto', cmap='viridis')
plt.colorbar(pcm, label='Normalized Beam Level (dB)', extend='both')
plt.clim(-50, 0)  # Adjust this based on your data range
plt.title(f'Beampatterns across Frequencies and Angles: Mic Spacing-{d} m')
plt.xlabel('Angle (degrees)')
plt.ylabel('Frequency (Hz)')
plt.ylim(freq_lower, freq_top)
plt.show()
