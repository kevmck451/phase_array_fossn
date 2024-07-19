import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

def array_factor(N, d, wavelength, angles, steering_angle):
    theta = np.deg2rad(angles - steering_angle)
    k = 2 * np.pi / wavelength
    beta = k * d * np.sin(theta)
    epsilon = 1e-10
    af = np.abs(np.sin(N * beta / 2) / (N * np.sin(beta / 2) + epsilon))
    return af

# Array specifications
N = 12
d = 0.08
freq_lower = 100
freq_top = 4000
c = 343  # Speed of sound in air in meters per second

# Frequencies and angles grid setup
frequencies = np.arange(freq_lower, freq_top + 1, 10)
angles = np.linspace(-90, 90, 361)  # ensures 360 intervals

fig, ax = plt.subplots(figsize=(10, 5))
ax.set_title('Dynamic Beampattern Steering across Angles and Frequencies')
ax.set_xlabel('Angle (degrees)')
ax.set_ylabel('Frequency (Hz)')
ax.set_ylim(freq_lower, freq_top)
ax.set_xlim(-90, 90)

# Prepare initial data
wavelength = c / frequencies  # Calculate wavelength for each frequency
beam_levels = np.array([20 * np.log10(array_factor(N, d, w, angles[:-1], 0) + 1e-10) for w in wavelength])

# Adjust the calculation of X, Y to match expected dimensions for shading='flat'
X, Y = np.meshgrid(angles, np.linspace(freq_lower, freq_top, len(frequencies) + 1))

# Plotting the mesh with correct shading option
pcm = ax.pcolormesh(X, Y, beam_levels, shading='flat', cmap='viridis')
fig.colorbar(pcm, label='Normalized Beam Level (dB)', extend='both')

def animate(steering_angle):
    new_beam_levels = np.array([20 * np.log10(array_factor(N, d, w, angles[:-1], steering_angle) + 1e-10) for w in wavelength])
    pcm.set_array(new_beam_levels.ravel())  # Update array, now correctly sized

ani = FuncAnimation(fig, animate, frames=np.linspace(-90, 90, 180), interval=100, repeat=True)

plt.show()
