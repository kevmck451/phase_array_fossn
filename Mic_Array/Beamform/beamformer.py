from Mic_Array.FIR_Filter.mic_coordinates import generate_mic_coordinates
from Mic_Array.FIR_Filter.generate_fir_coeffs import generate_fir_coeffs
from Filters.high_pass import high_pass_filter
from Filters.save_to_wav import save_to_wav
from Filters.down_sample import downsample
from Filters.audio import Audio

from scipy.signal import convolve
from pathlib import Path
import numpy as np
import time



def map_channels_to_positions(audio_data):
    num_mics = 48
    num_samples = audio_data.shape[1]

    mapped_data = np.zeros((4, 12, num_samples))

    mic_positions = [
        (1, 0), (0, 0), (1, 1), (0, 1), (3, 0), (2, 0), (3, 1), (2, 1),
        (1, 2), (0, 2), (1, 3), (0, 3), (3, 2), (2, 2), (3, 3), (2, 3),
        (1, 4), (0, 4), (1, 5), (0, 5), (3, 4), (2, 4), (3, 5), (2, 5),
        (1, 6), (0, 6), (1, 7), (0, 7), (3, 6), (2, 6), (3, 7), (2, 7),
        (1, 8), (0, 8), (1, 9), (0, 9), (3, 8), (2, 8), (3, 9), (2, 9),
        (1, 10), (0, 10), (1, 11), (0, 11), (3, 10), (2, 10), (3, 11), (2, 11)
    ]

    for ch_index in range(num_mics):
        mic_x, mic_y = mic_positions[ch_index]
        mapped_data[mic_x, mic_y, :] = audio_data[ch_index, :]

    return mapped_data

def beamform(audio_data, fir_coeffs):
    rows, cols, num_samples = audio_data.shape
    num_coeffs = fir_coeffs.shape[2]

    assert rows * cols == fir_coeffs.shape[0] * fir_coeffs.shape[1], "Mismatch between audio data and FIR coefficients shape."

    beamformed_data = np.zeros(num_samples + num_coeffs - 1)

    for row_index in range(rows):
        for col_index in range(cols):
            filtered_signal = convolve(audio_data[row_index, col_index, :], fir_coeffs[row_index, col_index, :], mode='full')
            beamformed_data += filtered_signal

    # Normalize the beamformed data
    max_val = np.max(np.abs(beamformed_data))
    if max_val != 0:
        beamformed_data = beamformed_data / max_val

    return beamformed_data

def generate_beamformed_audio(mapped_audio_data, theta, phi, temp_F):
    print('generating fir coefficients')
    fir_coeffs = generate_fir_coeffs(mic_coords, theta, phi, temp_F)
    print('beamforming audio')
    beamformed_audio = beamform(mapped_audio_data, fir_coeffs)

    return beamformed_audio




if __name__ == '__main__':
    start_time = time.time()

    base_path = '/Users/KevMcK/Dropbox/2 Work/1 Optics Lab/2 FOSSN/Data'
    filepath = f'{base_path}/Tests/9_outdoor_testing/diesel_sweep.wav'

    filepath_save = f'{base_path}/Tests/13_beamformed'
    tag_index = '_(-90, 90)' # 1

    thetas = [-90, -80, -70, -60, -50, -40, -30, -20, -10, 0, 10, 20, 30, 40, 50, 60, 70, 80, 90]  # elevation angle: pos is right and neg is left
    phi = 0  # azimuth angle
    temp_F = 90  # temperature in Fahrenheit

    print('opening audio')
    audio = Audio(filepath=filepath, num_channels=48)
    print('generating mic coordinates')
    # angle is from behind array looking forward. center is (0, 0)
    mic_coords = generate_mic_coordinates()
    print('mapping audio channels')
    mapped_audio_data = map_channels_to_positions(audio.data)
    print('~' * 40)
    prep_time = time.time() - start_time

    # --------------------------------------------------------------

    bf_start_time = time.time()

    beamformed_audio_data = np.zeros((len(thetas), audio.num_samples+200))

    for i, theta in enumerate(thetas):
        beamformed_audio_data[i, :] = generate_beamformed_audio(mapped_audio_data, theta, phi, temp_F)
        print(f'Completed BF Data for {theta}')
        print('-' * 40)

    print(f'shape: {beamformed_audio_data.shape}')
    print(beamformed_audio_data)

    beamform_time = time.time() - bf_start_time

    # Processing and Packing Audio
    # --------------------------------------------------------------
    # Create the new filename
    print('packing audio')
    original_path = Path(filepath)
    # export_tag = f'_BF{tag_index}_{theta}-{phi}'
    export_tag = f'_BF{tag_index}'
    new_filename = original_path.stem + export_tag + original_path.suffix
    new_filepath = f'{filepath_save}/{new_filename}'

    # Save the filtered audio to the new file
    beamformed_audio_object = Audio(data=beamformed_audio_data, num_channels=(len(thetas)), sample_rate=48000)
    beamformed_audio_object.path = Path(new_filepath)

    # High Pass Filter
    print('Passing High Freq')
    bottom_cutoff_freq = 500
    beamformed_audio_object.data = high_pass_filter(beamformed_audio_object, bottom_cutoff_freq)

    # print('downsampling audio')
    # new_sample_rate = 12000
    # beamformed_audio_object.data = downsample(beamformed_audio_object, new_sample_rate)
    # beamformed_audio_object.sample_rate = new_sample_rate

    save_to_wav(beamformed_audio_object.data, beamformed_audio_object.sample_rate, beamformed_audio_object.num_channels, new_filepath)

    end_time = time.time()
    total_time = end_time - start_time

    print(f'Prep Time: {np.round(prep_time, 2)} secs')
    print(f'Beamform Time: {np.round((beamform_time/60), 2)} mins')
    print(f'Total Time: {np.round((total_time/60), 2)} mins')


