
from Filters.audio import Audio

import numpy as np
from pathlib import Path


def fahrenheit_to_celsius(fahrenheit):
    return (fahrenheit - 32) * 5.0 / 9.0

def calculate_speed_of_sound(temperature_celsius):
    return 331.3 + 0.606 * temperature_celsius

def create_steering_vector(array_shape, mic_spacing, frequency, speed_of_sound, direction):
    # Calculate the wavenumber
    wavelength = speed_of_sound / frequency
    k = 2 * np.pi / wavelength

    # Create grid of microphone positions
    num_mics = array_shape[0] * array_shape[1]
    x = np.arange(array_shape[1]) * mic_spacing
    y = np.arange(array_shape[0]) * mic_spacing
    xx, yy = np.meshgrid(x, y)

    # Flatten grid to get mic positions
    mic_positions = np.stack((xx.ravel(), yy.ravel()), axis=-1)

    # Calculate steering vector
    steering_vector = np.exp(1j * k * (mic_positions @ direction))
    return steering_vector / np.sqrt(num_mics)

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

def beamform(audio_data, steering_vector):
    num_samples = audio_data.shape[1]
    beamformed_output = np.zeros(num_samples, dtype=np.complex64)

    for i in range(audio_data.shape[0]):
        beamformed_output += steering_vector[i] * audio_data[i, :]

    return np.real(beamformed_output)

def norm(data, percentage):
    max_value = np.max(np.abs(data))
    if max_value == 0:
        raise Exception('Max Value is Zero')

    data = np.nan_to_num(data)

    return data / (max_value * (percentage / 100.0))

# -------------------
# MAIN --------------
# -------------------
def main():
    base_path = '/Users/KevMcK/Dropbox/2 Work/1 Optics Lab/2 FOSSN/Data'

    # filepath = f'{base_path}/Tests/5_outdoor_testing/07-12-2024_02-49-21_chunk_1.wav'
    filepath = f'{base_path}/Tests/7_hallway_tone/07-15-2024_03-25-28_chunk_1.wav'
    # filepath = f'{base_path}Tests/7_hallway_tone/07-15-2024_03-33-35_chunk_1.wav'

    temperature_fahrenheit = 74  # example temperature
    direction = np.array([45, 45]) # beamforming direction (0 degrees azimuth, 0 degrees elevation)
    export_tag = '_BF2_45-45'

    # Array configuration
    array_shape = (4, 12) # (rows, cols)
    mic_spacing = 0.08  # meters
    frequency = 2000  # Hz

    # Calculate speed of sound
    temperature_celsius = fahrenheit_to_celsius(temperature_fahrenheit)
    speed_of_sound = calculate_speed_of_sound(temperature_celsius)
    print(f'Speed of Sound: {speed_of_sound}')

    # Create steering vector
    steering_vector = create_steering_vector(array_shape, mic_spacing, frequency, speed_of_sound, direction)
    print('Creating Steering Vector')
    # print(steering_vector)

    # Map channels to their correct positions
    audio = Audio(filepath=filepath, num_channels=48)
    mapped_audio_data = map_channels_to_positions(audio.data)

    # Perform beamforming
    beamformed_audio = beamform(mapped_audio_data, steering_vector)
    print(f'Beamformed Audio Shape: {beamformed_audio.shape}')
    print('Normalizing')
    beamformed_audio = norm(beamformed_audio, 100)

    # Create the new filename
    original_path = Path(filepath)
    new_filename = original_path.stem + export_tag + original_path.suffix
    filepath_save = f'{base_path}/Tests/8_beamformed'
    new_filepath = f'{filepath_save}/{new_filename}'

    # Save the filtered audio to the new file
    beamformed_audio_object = Audio(data=beamformed_audio, num_channels=1, sample_rate=48000)
    beamformed_audio_object.path = Path(new_filepath)
    beamformed_audio_object.export()


if __name__ == '__main__':
    main()
