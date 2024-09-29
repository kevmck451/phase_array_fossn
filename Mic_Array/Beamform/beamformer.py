from Mic_Array.FIR_Filter.mic_coordinates import generate_mic_coordinates
from Mic_Array.FIR_Filter.generate_fir_coeffs import generate_fir_coeffs
import Mic_Array.array_config as array_config

from Filters.noise_reduction import noise_reduction_filter
from Filters.high_pass import high_pass_filter
from Filters.save_to_wav import save_to_wav
from Filters.down_sample import downsample
from Filters.normalize import normalize
from Filters.audio import Audio

from multiprocessing import Pool, cpu_count
from functools import partial
from scipy.signal import convolve
from pathlib import Path
import numpy as np
import time


def map_channels_to_positions(audio_data):
    num_mics = 48
    num_samples = audio_data.shape[1]

    mapped_data = np.zeros((4, 12, num_samples))

    for ch_index in range(num_mics):
        mic_x, mic_y = array_config.mic_positions[ch_index]
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

def generate_beamformed_audio(mapped_audio_data, theta, phi, temp_F, mic_coords):
    print(f'generating fir coefficients: {theta} | {phi}')
    fir_coeffs = generate_fir_coeffs(mic_coords, theta, phi, temp_F)
    print('beamforming audio')
    print('-' * 40)

    return beamform(mapped_audio_data, fir_coeffs)

def generate_beamformed_audio_iterative(mapped_audio_data, thetas, phis, temp_F, mic_coords):
    beamformed_audio_data = np.zeros((len(thetas), audio.num_samples+200))
    for i, theta in enumerate(thetas):
        beamformed_audio_data[i, :] = generate_beamformed_audio(mapped_audio_data, theta, phis[0], temp_F, mic_coords)
        print(f'Completed BF Data for {theta}')
        print('-' * 40)

    return beamformed_audio_data

def generate_beamformed_audio_parallel(theta, mapped_audio_data, phi, temp_F, mic_coords):
    return generate_beamformed_audio(mapped_audio_data, theta, phi, temp_F, mic_coords)

def optimize_beamforming(thetas, mapped_audio_data, phi, temp_F, mic_coords):
    beamformed_audio_data = np.zeros((len(thetas), audio.num_samples + 200))

    # Create a partial function with the fixed arguments
    partial_func = partial(generate_beamformed_audio_parallel, mapped_audio_data=mapped_audio_data, phi=phi, temp_F=temp_F, mic_coords=mic_coords)

    with Pool(cpu_count()) as p:
        results = p.map(partial_func, thetas)

    for i, result in enumerate(results):
        beamformed_audio_data[i, :] = result
        print(f'Completed BF Data for {i}')

    return beamformed_audio_data

# -------------------------------------------------------------------------------------------------------------------
if __name__ == '__main__':
    start_time = time.time()

    base_path = '/Users/KevMcK/Dropbox/2 Work/1 Optics Lab/2 FOSSN/Data'
    # filepath = f'{base_path}/Tests/17_outdoor_testing/cars_drive_by_150m.wav'
    # filepath = f'{base_path}/Tests/17_outdoor_testing/distance_160-50m.wav'
    # filepath = f'{base_path}/Tests/17_outdoor_testing/sweep_angel_100m.wav'
    # filepath = f'{base_path}/Tests/17_outdoor_testing/sweep_semi_100m.wav'

    filename = '09-25-2024_10-54-17_chunk_1'
    filepath = f'{base_path}/Field_Tests/9-25 Field Test/Data/9-25-24 10.42am/Audio_10.54am/{filename}.wav'



    filepath_save = f'{base_path}/Analysis/angel_beamforming'
    tag_index = '_(-70, 70)-(0)'

    # elevation angle: neg is left and pos is right
    # thetas = [-40,-30,-20,-10, 0, 10, 20,30,40]
    thetas = [-70, -60, -50, -40, -30, -20, -10, 0, 10, 20, 30, 40, 50, 60, 70]
    phis = [0]  # azimuth angle: neg is below and pos is above
    temp_F = 74  # temperature in Fahrenheit

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

    # Iterative Method: takes longer time
    beamformed_audio_data = generate_beamformed_audio_iterative(mapped_audio_data, thetas, phis, temp_F, mic_coords)

    # Parallel Method: much shorter time
    # list_of_data = list()
    # for phi in phis:
    #     beamformed_audio_data = optimize_beamforming(thetas, mapped_audio_data, phi, temp_F, mic_coords)
    #     list_of_data.append(beamformed_audio_data)
    #     print('-' * 40)
    # beamformed_audio_data = np.vstack(list_of_data)


    print(f'shape: {beamformed_audio_data.shape}')

    beamform_time = time.time() - bf_start_time

    # --------------------------------------------------------------
    print('packing audio')
    original_path = Path(filepath)
    # export_tag = f'_BF{tag_index}_{theta}-{phi}'
    export_tag = f'_BF{tag_index}'
    new_filename = original_path.stem + export_tag + original_path.suffix
    new_filepath = f'{filepath_save}/{new_filename}'

    # Save the filtered audio to the new file
    beamformed_audio_object = Audio(data=beamformed_audio_data, num_channels=(len(thetas)*len(phis)), sample_rate=48000)
    beamformed_audio_object.path = Path(new_filepath)

    # --------------------------------------------------------------
    # print('Reducing Noise')
    # std_threshold = 0.5
    # audio.data = noise_reduction_filter(audio, std_threshold)

    print('Passing High Freq')
    bottom_cutoff_freq = 1000
    beamformed_audio_object.data = high_pass_filter(beamformed_audio_object, bottom_cutoff_freq)

    print('Normalizing')
    percentage = 100
    beamformed_audio_object.data = normalize(beamformed_audio_object, percentage)

    print('downsampling audio')
    new_sample_rate = 6000
    beamformed_audio_object.data = downsample(beamformed_audio_object, new_sample_rate)
    beamformed_audio_object.sample_rate = new_sample_rate

    save_to_wav(beamformed_audio_object.data, beamformed_audio_object.sample_rate, beamformed_audio_object.num_channels, new_filepath)

    end_time = time.time()
    total_time = end_time - start_time

    print(f'Prep Time: {np.round(prep_time, 2)} secs')
    print(f'Beamform Time: {np.round((beamform_time/60), 2)} mins')
    print(f'Total Time: {np.round((total_time/60), 2)} mins')