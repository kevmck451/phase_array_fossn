from Mic_Array.FIR_Filter.mic_coordinates import generate_mic_coordinates
from Mic_Array.FIR_Filter.generate_fir_coeffs import generate_fir_coeffs
from Filters.audio import Audio

from pathlib import Path
import numpy as np


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

def beamform(audio_data, fir_coeffs):
    beamformed_data = 0

    return beamformed_data




def norm(data, percentage):
    max_value = np.max(np.abs(data))
    if max_value == 0:
        raise Exception('Max Value is Zero')

    data = np.nan_to_num(data)

    return data / (max_value * (percentage / 100.0))



if __name__ == '__main__':

    base_path = '/Users/KevMcK/Dropbox/2 Work/1 Optics Lab/2 FOSSN/Data'
    filepath = f'{base_path}/Tests/11_outdoor_testing/07-22-2024_01-36-01_chunk_1.wav'

    tag_index = 1
    filepath_save = f'{base_path}/Tests/12_beamformed'

    audio = Audio(filepath=filepath, num_channels=48)
    mapped_audio_data = map_channels_to_positions(audio.data)

    # angle is from behind array looking forward. center is (0, 0)
    mic_coords = generate_mic_coordinates()
    theta = 0  # elevation angle
    phi = 0  # azimuth angle
    temp_F = 95  # temperature in Fahrenheit
    sample_rate = 48000

    fir_coeffs = generate_fir_coeffs(mic_coords, theta, phi, temp_F, sample_rate)
    print(fir_coeffs.shape)

    # Perform beamforming
    beamformed_audio = beamform(mapped_audio_data, fir_coeffs)
    print(f'Beamformed Audio Shape: {beamformed_audio.shape}')
    print('Normalizing')
    beamformed_audio = norm(beamformed_audio, 100)

    # Create the new filename
    original_path = Path(filepath)
    export_tag = f'_BF{tag_index}_{theta}-{phi}'
    new_filename = original_path.stem + export_tag + original_path.suffix

    new_filepath = f'{filepath_save}/{new_filename}'
    # Save the filtered audio to the new file
    beamformed_audio_object = Audio(data=beamformed_audio, num_channels=1, sample_rate=48000)
    beamformed_audio_object.path = Path(new_filepath)
    beamformed_audio_object.export()


