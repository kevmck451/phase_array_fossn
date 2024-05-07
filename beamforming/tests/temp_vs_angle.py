import numpy as np
import matplotlib.pyplot as plt


def fahrenheit_to_celsius(temp_fahrenheit):
    """Convert Fahrenheit to Celsius."""
    return (temp_fahrenheit - 32) * 5.0 / 9.0


def speed_of_sound(temp_celsius):
    """Calculate the speed of sound based on temperature in Celsius."""
    return 331.3 + 0.606 * temp_celsius


def perceived_angle(true_speed, measured_speed, true_angle_deg):
    """Calculate the perceived angle based on the actual and measured speeds of sound."""
    true_angle_rad = np.radians(true_angle_deg)
    sin_true_angle = np.sin(true_angle_rad)
    perceived_sin_angle = sin_true_angle * (true_speed / measured_speed)
    perceived_sin_angle = np.clip(perceived_sin_angle, -1, 1)  # Clipping to avoid numerical issues
    perceived_angle_rad = np.arcsin(perceived_sin_angle)
    return np.degrees(perceived_angle_rad)


def angle_error(true_angle, perceived_angle):
    """Calculate the angular error."""
    return perceived_angle - true_angle


# Parameters
standard_temp_f = 68  # Standard temperature in Fahrenheit
standard_speed = speed_of_sound(fahrenheit_to_celsius(standard_temp_f))

# Temperature range from 35 to 110 degrees Fahrenheit
temps_f = np.linspace(35, 110, 6)  # Fewer points for clarity in visualization

# Angles from -90 to 90 degrees
angles_deg = np.linspace(-90, 90, 180)

# Initialize plot
plt.figure(figsize=(12, 8))

for temp_f in temps_f:
    temp_c = fahrenheit_to_celsius(temp_f)
    current_speed = speed_of_sound(temp_c)
    perceived_angles = [perceived_angle(standard_speed, current_speed, ang) for ang in angles_deg]
    errors = [angle_error(ang, perc_ang) for ang, perc_ang in zip(angles_deg, perceived_angles)]

    plt.plot(angles_deg, errors, label=f'Temp = {temp_f}°F')

plt.title('Angular Error vs. Angle for Various Temperatures')
plt.xlabel('True Angle (Degrees)')
plt.ylabel('Angular Error (Degrees)')
plt.axhline(y=0, color='black', linestyle='--')  # Line to indicate zero error
plt.legend(title='Temperature')
plt.grid(True)
plt.show()
