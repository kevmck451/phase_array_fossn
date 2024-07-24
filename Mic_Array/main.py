from mic_coordinates import generate_mic_coordinates
from time_delays import calculate_time_delays



# uses info from array_config
mic_coordinates = generate_mic_coordinates()

# angle is from behind array looking forward. center is (0, 0)
theta = 1  # elevation angle
phi = 0  # azimuth angle
temperature_F = 95  # temperature in Fahrenheit

time_delays = calculate_time_delays(mic_coordinates, theta, phi, temperature_F)
