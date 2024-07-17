from Filters.audio import Audio

import numpy as np
from pathlib import Path

def fahrenheit_to_celsius(fahrenheit):
    return (fahrenheit - 32) * 5.0 / 9.0

def calculate_speed_of_sound(temperature_celsius):
    return 331.3 + 0.606 * temperature_celsius

def create_steering_vector(array_shape, mic_spacing, frequency, speed_of_sound, azimuth, elevation):
    # Convert azimuth and elevation to radians
    azimuth_rad = np.radians(azimuth)
    elevation_rad = np.radians(elevation)

    # Calculate the direction cosines
    dx = np.cos(elevation_rad) * np.cos(azimuth_rad)
    dy = np.cos(elevation_rad) * np.sin(azimuth_rad)
    dz = np.sin(elevation_rad)

    direction = np.array([dx, dy, dz])

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
    # The steering vector calculation involves the dot product of mic_positions and direction
    steering_vector = np.exp(1j * k * (mic_positions @ direction[:2]))
    return steering_vector / np.sqrt(num_mics)

def map_channels_to_positions(audio_data):
    num_mics = 48
    num_samples = audio_data.shape[1]
    mapped_data = np.zeros((num_mics, num_samples))

    antenna_offsets = [(0, 0), (0, 2), (0, 4), (2, 0), (2, 2), (2, 4)]
    channel_order = [(1, 0), (0, 0), (1, 1), (0, 1), (3, 0), (2, 0), (3, 1), (2, 1)]

    for i in range(6):
        offset_x, offset_y = antenna_offsets[i]
        for j in range(8):
            mic_x = offset_x + channel_order[j][0]
            mic_y = (offset_y // 2) + channel_order[j][1]
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
    if (max_value == 0):
        raise Exception('Max Value is Zero')

    data = np.nan_to_num(data)

    return data / (max_value * (percentage / 100.0))

def main():
    base_path = '/Users/KevMcK/Dropbox/2 Work/1 Optics Lab/2 FOSSN/Data'
    filepath = f'{base_path}/Tests/9_outdoor_testing/07-16-2024_03-25-22_chunk_1.wav'

    temperature_fahrenheit = 95  # example temperature
    azimuth = 60  # degrees -80 to 80
    elevation = 0  # degrees 0 - 60
    tag_index = 3
    filepath_save = f'{base_path}/Tests/10_beamformed'

    # Array configuration
    array_shape = (4, 12) # (rows, cols)
    mic_spacing = 0.08  # meters
    frequency = 2000  # Hz

    # Calculate speed of sound
    temperature_celsius = fahrenheit_to_celsius(temperature_fahrenheit)
    speed_of_sound = calculate_speed_of_sound(temperature_celsius)
    print(f'Speed of Sound: {speed_of_sound}')

    # Create steering vector
    steering_vector = create_steering_vector(array_shape, mic_spacing, frequency, speed_of_sound, azimuth, elevation)
    print('Creating Steering Vector')

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
    export_tag = f'_BF{tag_index}_{azimuth}-{elevation}'
    new_filename = original_path.stem + export_tag + original_path.suffix
    new_filepath = f'{filepath_save}/{new_filename}'

    # Save the filtered audio to the new file
    beamformed_audio_object = Audio(data=beamformed_audio, num_channels=1, sample_rate=48000)
    beamformed_audio_object.path = Path(new_filepath)
    beamformed_audio_object.export()

if __name__ == '__main__':
    main()
