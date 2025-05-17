

import numpy as np
import math

def calculate_speed_of_sound(temperature_F):
    temperature_celsius = (temperature_F - 32) * 5.0 / 9.0
    return 331.3 + 0.606 * temperature_celsius

def calculate_directional_cosines(theta, phi):

    # Directional cosines are the cosines of the angles between a vector and the coordinate axes.
    # They describe the direction of a vector in a 3D space.

    wx = math.cos(math.radians(phi)) * math.sin(math.radians(theta))
    wy = math.sin(math.radians(phi))
    wz = math.cos(math.radians(phi)) * math.cos(math.radians(theta))

    # print(f"Directional cosines: x={wx}, y={wy}, z={wz}")
    return wx, wy, wz

def calculate_time_delays(mic_positions, theta, phi, temperature_F, array_config, beam_mix):
    """
    Calculate time delays for each microphone.

    Args:
    - mic_positions (ndarray): Positions of microphones in the form (num_mics, 3) for x, y, z.
    - theta (float): Elevation angle in degrees.
    - phi (float): Azimuth angle in degrees.
    - temperature_F (float): Air temperature in Fahrenheit.

    Returns:
    - ndarray: Time delays for each microphone in micro seconds
    """

    # Calculate directional cosines
    wx, wy, wz = calculate_directional_cosines(theta, phi)

    speed_of_sound = calculate_speed_of_sound(temperature_F)

    # Calculate path differences and time delays
    # path diff is dot product of mic pos vector and directional cos vector
    # divide by rate to convert to time
    time_delays = np.zeros(mic_positions.shape[0])

    # The reference position is (0, 0, 0) in this centered coordinate system
    ref_position = np.array([0.0, 0.0, 0.0])

    for i, mic_pos in enumerate(mic_positions):
        relative_position = mic_pos - ref_position
        dt = (wx * relative_position[0] + wy * relative_position[1] + wz * relative_position[2]) / speed_of_sound
        # time_delays[i] = dt * 1e6  # convert to microseconds
        time_delays[i] = dt * array_config.sample_rate  # convert to sample delay

    # reshape to grid
    time_delays = time_delays.reshape(beam_mix.rows, beam_mix.cols)

    return time_delays



