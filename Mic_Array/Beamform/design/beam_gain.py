import numpy as np


def calculate_wavelength_from_spacing(d):
    # Calculate the wavelength based on the spacing
    return 2 * d


def calculate_array_factor(num_rows, num_cols, d, wavelength, azimuth, elevation):
    k = 2 * np.pi / wavelength  # Wave number
    array_factor = 0.0 + 0.0j  # Initialize complex array factor

    # Loop through each element in the array
    for row in range(num_rows):
        for col in range(num_cols):
            # Position of each element
            x = col * d
            y = row * d

            # Calculate phase shift based on azimuth and elevation
            phase_shift = k * (x * np.sin(elevation) * np.cos(azimuth) + y * np.sin(elevation) * np.sin(azimuth))
            array_factor += np.exp(1j * phase_shift)

    return np.abs(array_factor) ** 2  # Return the squared magnitude for gain


def calculate_average_main_lobe_gain(num_rows, num_cols, d, frequency, azimuth_angles, elevation_angles):
    wavelength = calculate_wavelength_from_spacing(d)

    # Calculate gain for each angle and store it
    gains = []

    for azimuth in azimuth_angles:
        for elevation in elevation_angles:
            # Convert angles to radians
            azimuth_rad = np.deg2rad(azimuth)
            elevation_rad = np.deg2rad(elevation)

            # Calculate the main lobe gain at the current angle
            gain = calculate_array_factor(num_rows, num_cols, d, wavelength, azimuth_rad, elevation_rad)
            gains.append(gain)

    # Calculate the average of all main lobe gains
    average_gain = np.mean(gains)

    return average_gain


# Parameters
num_rows = 4
num_cols = 12
d = 0.08  # Spacing in meters
frequency = 343 / (2 * d)  # Rough frequency based on spacing for air
azimuth_angles = np.arange(0, 360, 10)  # Azimuth angles from 0 to 360 degrees
elevation_angles = np.array([0])  # Only consider horizontal plane for simplicity

# Calculate average main lobe gain
average_gain = calculate_average_main_lobe_gain(num_rows, num_cols, d, frequency, azimuth_angles, elevation_angles)

# Convert to dB
average_gain_in_db = 10 * np.log10(average_gain)

# Output results
print(f"Average gain of the main lobes: {average_gain:.2f}")
print(f"Average gain increase (dB): {average_gain_in_db:.2f} dB")
