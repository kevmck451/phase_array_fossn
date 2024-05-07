




# Example usage
speed_of_sound = 343.0  # Speed of sound in air at 20 degrees Celsius in m/s
target_frequency = 2000.0  # Target frequency in Hz

wavelength = speed_of_sound / target_frequency
spacing = wavelength / 2
print(f"Optimal microphone spacing for {target_frequency} Hz is {spacing:.4f} meters.")
