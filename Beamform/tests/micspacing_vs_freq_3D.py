import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D


def array_factor(N, d, wavelength, angles):
    """
    Calculate the array factor for a linear array over a range of angles.

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
    # Avoid division by zero
    with np.errstate(divide='ignore', invalid='ignore'):
        af = np.abs(np.sin(N * beta / 2) / (N * np.sin(beta / 2)))
        af[np.isnan(af)] = 0  # Replace NaNs with 0 for stability
    return af.max()


# Array specifications
N = 12  # Number of microphones
distances = np.arange(0.05, 0.15, 0.01)  # Spacing between microphones in meters
frequencies = np.arange(500, 5000, 100)  # Frequencies in Hz
c = 343  # Speed of sound in air in m/s
angles = np.linspace(-90, 90, 180)  # Angle range for maximum calculation

# Prepare data for 3D plot
D, F = np.meshgrid(distances, frequencies)
AF = np.zeros_like(D)

for i in range(F.shape[0]):
    for j in range(F.shape[1]):
        wavelength = c / F[i, j]
        AF[i, j] = array_factor(N, D[i, j], wavelength, angles)

# Plotting
fig = plt.figure(figsize=(12, 8))
ax = fig.add_subplot(111, projection='3d')
surf = ax.plot_surface(D, F, 20 * np.log10(AF), cmap='viridis', edgecolor='none')
ax.set_xlabel('Microphone Spacing (m)')
ax.set_ylabel('Frequency (Hz)')
ax.set_zlabel('Maximum Gain (dB)')
ax.set_title('Maximum Directivity as a Function of Frequency and Microphone Spacing')
fig.colorbar(surf, ax=ax, shrink=0.5, aspect=5)
plt.show()
