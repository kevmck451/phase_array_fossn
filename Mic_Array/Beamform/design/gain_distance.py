import numpy as np
import matplotlib.pyplot as plt

def calculate_intensity(power, distance):
    """ Calculate intensity using the inverse square law. """
    return power / (4 * np.pi * distance**2)

def calculate_effective_intensity(intensity, gain):
    """ Calculate effective intensity using the microphone's gain. """
    return intensity * gain

def main():
    # Constants
    power = 100.0  # Increased power of the sound source in watts (e.g., 100W)
    average_gain = 10.0  # Increased average main lobe gain (example: 10 for good sensitivity)

    # Define a range of distances (1 to 1000 meters)
    distances = np.linspace(1, 1000, 1000)  # 1000 points between 1 and 1000 meters
    effective_intensities = []

    # Calculate effective intensity for each distance
    for distance in distances:
        intensity = calculate_intensity(power, distance)
        effective_intensity = calculate_effective_intensity(intensity, average_gain)
        effective_intensities.append(effective_intensity)

    # Convert effective intensities to numpy array for plotting
    effective_intensities = np.array(effective_intensities)

    # Plot effective intensities
    plt.figure(figsize=(12, 6))
    plt.plot(distances, effective_intensities, label='Effective Intensity from Phased Array', color='blue')

    # Add target intensity lines (you can adjust these values)
    target_intensities = [0.01, 0.1, 1.0]  # Target intensities in W/m²
    for target in target_intensities:
        plt.axhline(y=target, color='red', linestyle='--', label=f'Target Intensity: {target} W/m²')

    # Labels and titles
    plt.title('Effective Intensity of Sound Detected by Phased Array Microphone')
    plt.xlabel('Distance (m)')
    plt.ylabel('Effective Intensity (W/m²)')
    plt.yscale('log')  # Use logarithmic scale for better visualization
    plt.grid(True)
    plt.legend()
    plt.xlim(0, 1000)
    plt.ylim(1e-4, 10)  # Adjust y-limits for visibility
    plt.show()

if __name__ == "__main__":
    main()
