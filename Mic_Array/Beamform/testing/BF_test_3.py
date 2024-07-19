
from Filters.audio import Audio

from pathlib import Path
from tqdm import tqdm
import numpy as np
import math


def map_channels_to_positions(audio_data):
    # Mapping based on the provided channel configuration
    # Each antenna has 8 microphones in a 4x2 configuration:
    # ch1 (1,0), ch2 (0,0), ch3 (1,1), ch4 (0,1), ch5 (3,0), ch6 (2,0), ch7 (3,1), ch8 (2,1)

    num_mics = 48
    num_samples = audio_data.shape[1]

    mapped_data = np.zeros((num_mics, num_samples))

    # Corrected mapping
    antenna_offsets = [(0, 0), (0, 2), (0, 4), (2, 0), (2, 2), (2, 4)]
    channel_order = [(1, 0), (0, 0), (1, 1), (0, 1), (3, 0), (2, 0), (3, 1), (2, 1)]

    for i in range(6):
        offset_x, offset_y = antenna_offsets[i]
        for j in range(8):
            mic_x = offset_x + channel_order[j][0]
            mic_y = (offset_y // 2) + channel_order[j][1]  # Adjusted to stay within 4 rows
            mic_index = mic_y * 12 + mic_x
            if mic_index >= num_mics:
                raise IndexError(f"Calculated mic_index {mic_index} is out of bounds for array size {num_mics}")
            mapped_data[mic_index, :] = audio_data[i * 8 + j, :]

    return mapped_data

def fahrenheit_to_celsius(fahrenheit):
    return (fahrenheit - 32) * 5.0 / 9.0

def calculate_speed_of_sound(temperature_celsius):
    return 331.3 + 0.606 * temperature_celsius

def calculate_delay(x, y, z, theta, phi, sample_rate, speed_of_sound):
    wx = math.cos(math.radians(phi)) * math.cos(math.radians(theta))
    wy = math.cos(math.radians(phi)) * math.sin(math.radians(theta))
    wz = math.sin(math.radians(phi))

    dt = ((wx * x) + (wy * y) + (wz * z)) / speed_of_sound
    delay = (dt * sample_rate) - 0.5

    return delay

def calculate_tap_weights(delay, filter_length, win_length):
    tapWeight = np.zeros(filter_length)
    centerTap = win_length / 2
    for i in range(filter_length):
        x = i - delay
        sinc = np.sinc(x - centerTap)
        window = 0.54 - (0.46 * np.cos(2.0 * math.pi * (x + 0.5) / win_length))
        tapWeight[i] = window * sinc

    return tapWeight

def create_taps_weights(array_shape, mic_spacing, speed_of_sound, azimuth, elevation):
    # Parameters
    sample_rate = 48000
    filter_length = 101
    win_length = 25

    # Create grid of microphone positions
    num_mics = array_shape[0] * array_shape[1]
    x = np.arange(array_shape[1]) * mic_spacing
    y = np.arange(array_shape[0]) * mic_spacing
    xx, yy = np.meshgrid(x, y)
    mic_positions = np.stack((xx.ravel(), yy.ravel()), axis=-1)

    # Calculate delays and tap weights for each microphone
    delays = np.zeros(num_mics)
    tap_weights = np.zeros((num_mics, filter_length))

    for i, (mx, my) in enumerate(mic_positions):
        delays[i] = calculate_delay(mx, my, 0, azimuth, elevation, sample_rate, speed_of_sound)
        tap_weights[i] = calculate_tap_weights(delays[i], filter_length, win_length)

    return tap_weights

def norm(data, percentage):
    max_value = np.max(np.abs(data))
    if max_value == 0:
        raise Exception('Max Value is Zero')

    data = np.nan_to_num(data)

    return data / (max_value * (percentage / 100.0))

# -----------------------------------------------------------------------
def main():
    base_path = '/Users/KevMcK/Dropbox/2 Work/1 Optics Lab/2 FOSSN/Data'

    filepath = f'{base_path}/Tests/9_outdoor_testing/07-16-2024_03-25-22_chunk_1.wav'

    temperature_fahrenheit = 95  # example temperature
    azimuth = -60  # degrees -80 to 80
    elevation = 0  # degrees 0 - 60
    tag_index = 4
    filepath_save = f'{base_path}/Tests/10_beamformed'

    # Array configuration
    array_shape = (4, 12)  # (rows, cols)
    mic_spacing = 0.08  # meters

    # Calculate speed of sound based on temperature
    temperature_celsius = fahrenheit_to_celsius(temperature_fahrenheit)
    speed_of_sound = calculate_speed_of_sound(temperature_celsius)
    print('Speed of Sound:', speed_of_sound)

    # Create steering vector (tap weights in this case)
    print('Creating Tap Weights')
    tap_weights = create_taps_weights(array_shape, mic_spacing, speed_of_sound, azimuth, elevation)

    # print(tap_weights)

    # Map channels to their correct positions
    audio = Audio(filepath=filepath, num_channels=48)
    mapped_audio_data = map_channels_to_positions(audio.data)

    # Apply tap weights for beamforming
    beamformed_audio = np.zeros(mapped_audio_data.shape[1])
    for i in range(mapped_audio_data.shape[0]):
        beamformed_audio += np.convolve(mapped_audio_data[i], tap_weights[i], mode='same')

    print(f'Beamformed Audio Shape: {beamformed_audio.shape}')
    print('Normalizing')
    beamformed_audio = norm(beamformed_audio, 100)

    # Create the new filename
    original_path = Path(filepath)
    export_tag = f'_BF{tag_index}_{azimuth}-{elevation}'
    new_filename = original_path.stem + export_tag + original_path.suffix

    new_filepath = f'{filepath_save}/{new_filename}'
    # Save the filtered audio to the new file
    beamformed_audio_object = Audio(data=beamformed_audio, num_channels=1, sample_rate=48000)
    beamformed_audio_object.path = Path(new_filepath)
    beamformed_audio_object.export()

if __name__ == '__main__':
    main()
