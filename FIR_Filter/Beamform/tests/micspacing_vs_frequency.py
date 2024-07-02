import numpy as np
import matplotlib.pyplot as plt


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
d = 0.05  # Spacing between microphones in meters
# distances = np.arange(0.05, 0.15, 0.01)  # Spacing between microphones in meters

# Frequencies to examine
# freq_lower = 100
# freq_top = 1000
freq_lower = 1000
freq_top = 2000

frequencies = np.arange(freq_lower, freq_top+1, 100)  # Frequencies in Hz
c = 343  # Speed of sound in air in m/s

# Angle range for plotting
angles = np.linspace(-90, 90, 360)

plt.figure(figsize=(10, 8))
for f in frequencies:
    wavelength = c / f
    af = array_factor(N, d, wavelength, angles)
    plt.plot(angles, 20 * np.log10(af), label=f'{f} Hz')

plt.title('Beampattern of Linear Microphone Array')
plt.xlabel('Angle (degrees)')
plt.ylabel('Normalized Beam Level (dB)')
plt.grid(True)
plt.legend(loc='lower right')
plt.ylim([-60, 0])
plt.show()
# plt.savefig(f'/Users/KevMcK/Dropbox/2 Work/1 Optics Lab/2 FOSSN/Analysis/Beamforming/beam pattern {freq_lower}-{freq_top}.png', dpi=300)
