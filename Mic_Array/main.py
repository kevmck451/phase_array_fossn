from mic_coordinates import generate_mic_coordinates
from time_delays import calculate_time_delays
from fir_filter import create_fir_filters



# uses info from array_config
mic_coordinates = generate_mic_coordinates()

# angle is from behind array looking forward. center is (0, 0)
theta = 0  # elevation angle
phi = 0  # azimuth angle
temperature_F = 95  # temperature in Fahrenheit
sample_rate = 48000

time_delays = calculate_time_delays(mic_coordinates, theta, phi, temperature_F, sample_rate)
print(time_delays.shape)
num_taps = 100

fir_filter = create_fir_filters(time_delays, num_taps)
print(fir_filter.shape)
print(fir_filter)




