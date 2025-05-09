

import Application.engine.beamform.mic_coordinates as mic_coord

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

def calculate_time_delays(mic_positions, theta, phi, temperature_F, array_config):
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
    time_delays = time_delays.reshape(array_config.rows, array_config.cols)

    return time_delays







# Example usage
if __name__ == '__main__':
    from Application.engine.beamform.mic_coordinates import generate_mic_coordinates

    mic_coordinates = generate_mic_coordinates()
    theta = 90  # example elevation angle
    phi = 90  # example azimuth angle
    temperature_F = 95  # example temperature in Fahrenheit
    sample_rate = 48000

    time_delays = calculate_time_delays(mic_coordinates, theta, phi, temperature_F, sample_rate)
    # print(f"Time delays: {time_delays}")

    # Print the coordinates to verify they are correct
    print("Microphone coordinates in a 4x12 grid:")
    for row in range(4):
        for col in range(12):
            idx = row * 12 + col
            x, y, z = mic_coordinates[idx]
            print(f'({x:.3f}, {y:.3f})', end='\t ')
        print()  # Newline at the end of each row

    # Example angles
    angles = [(0, 0), (90, 0), (-90, 0), (180, 0), (90, 90), (-90, -90), (45, 0), (-45, 0), (45, 45), (1, 0)]
    temperature_F = 95  # example temperature in Fahrenheit

    max = 0

    for theta, phi in angles:
        print(f"\nTheta: {theta}, Phi: {phi}")
        time_delays = calculate_time_delays(mic_coordinates, theta, phi, temperature_F, sample_rate)
        max_temp = np.max(np.abs(time_delays))
        # Print the time delays in a 4x12 array format
        print("Time delays (in samples):")
        for row in time_delays:
            print("\t".join(f"{delay:.6f}" for delay in row))