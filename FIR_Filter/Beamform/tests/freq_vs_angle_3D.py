import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

def array_factor(N, d, wavelength, angles):
    """
    Calculate the array factor for a linear array.

    Parameters:
    N : int
        Number of microphones in the array.
    d : float
        Distance between adjacent microphones.
    wavelength : float
        Wavelength of the sound.
    angles : np.array
        Angles (in degrees) at which to calculate the array factor.

    Returns:
    np.array
        The array factor at each angle.
    """
    # Convert angles from degrees to radians
    theta = np.deg2rad(angles)
    # Calculate the wavenumber
    k = 2 * np.pi / wavelength
    # Array phase difference
    beta = k * d * np.sin(theta)
    # Array factor calculation using formula for linear array
    af = np.abs(np.sin(N * beta / 2) / (N * np.sin(beta / 2)))
    return af

# Array specifications
N = 12  # Number of microphones
d = 0.08  # Spacing between microphones in meters
freq_lower = 100
freq_top = 4000
frequencies = np.arange(freq_lower, freq_top + 1, 10)  # Frequencies in Hz
c = 343  # Speed of sound in air in m/s
angles = np.linspace(-90, 90, 360)  # Angle range for plotting

# Prepare data for the 3D plot
beam_levels = np.zeros((len(frequencies), len(angles)))

for i, f in enumerate(frequencies):
    wavelength = c / f
    af = array_factor(N, d, wavelength, angles)
    beam_levels[i, :] = 20 * np.log10(af)

# Create a meshgrid for 3D plotting
A, F = np.meshgrid(angles, frequencies)

# Plotting
fig = plt.figure(figsize=(14, 8))
ax = fig.add_subplot(111, projection='3d')
surf = ax.plot_surface(A, F, beam_levels, cmap='viridis', edgecolor='none')
ax.set_xlabel('Angle (degrees)')
ax.set_ylabel('Frequency (Hz)')
ax.set_zlabel('Beam Level (dB)')
ax.set_title(f'Beampatterns across Frequencies and Angles: Mic Spacing-{d}')
fig.colorbar(surf, ax=ax, shrink=0.5, aspect=5)
plt.show()
