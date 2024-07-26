
from Filters.noise_reduction import noise_reduction_filter
from Filters.spectral_whitening import spectral_whitening
from Filters.high_pass import high_pass_filter
from Filters.low_pass import low_pass_filter
from Filters.normalize import normalize
from Filters.down_sample import downsample
from Filters.save_to_wav import save_to_wav

from Filters.audio import Audio

from pathlib import Path
import numpy as np


def process_audio(audio, processing_list):
    normalize_percentage = 100
    new_sample_rate = 12000
    std_threshold = 0.5
    bottom_cutoff_freq = 500
    top_cutoff_freq = 3000


    print('Spectral Whitening')
    audio.data = spectral_whitening(audio)
    # print('Reducing Noise')
    # audio.data = noise_reduction_filter(audio, std_threshold)
    # print('Passing High Freq')
    # audio.data = high_pass_filter(audio, bottom_cutoff_freq, order=8)
    # print('Pass Low Freq')
    # audio.data = low_pass_filter(audio, top_cutoff_freq, order=8)
    # print('Reducing Noise')
    # audio.data = noise_reduction_filter(audio)
    # print('Normalizing')
    # audio.data = normalize(audio, normalize_percentage)
    # print('Down Sampling')
    # audio.data = downsample(audio, new_sample_rate)
    # audio.sample_rate = new_sample_rate





    return audio


if __name__ == '__main__':
    base_path = '/Users/KevMcK/Dropbox/2 Work/1 Optics Lab/2 FOSSN/Data'

    # filepath = '/Users/KevMcK/Dropbox/2 Work/1 Optics Lab/2 FOSSN/Data/Tests/5_outdoor_testing/07-12-2024_02-49-21_chunk_1.wav'
    # filepath = '/Users/KevMcK/Dropbox/2 Work/1 Optics Lab/2 FOSSN/Data/Tests/7_hallway_tone/07-15-2024_03-25-28_chunk_1.wav'

    # filepath = '/Users/KevMcK/Dropbox/2 Work/1 Optics Lab/2 FOSSN/Data/Tests/7_hallway_tone/07-15-2024_03-33-35_chunk_1.wav'
    # audio = Audio(filepath=filepath, num_channels=48)

    # filepath = '/Users/KevMcK/Dropbox/2 Work/1 Optics Lab/2 FOSSN/Data/Tests/11_outdoor_testing/07-22-2024_01-36-01_chunk_1_MONO19.wav'

    filepath = f'{base_path}/Tests/13_beamformed/diesel_sweep_BF_(-90, 90)-(0, 30).wav'
    audio = Audio(filepath=filepath, num_channels=114)

    export_tag = '_Pro3'
    filepath_save = f'{base_path}/Tests/13_beamformed'

    shape_og = audio.data.shape
    # print(audio)

    std_threshold = 2
    bottom_cutoff_freq = 500
    top_cutoff_freq = 3000
    normalize_percentage = 100
    new_sample_rate = 12000

    print('Reducing Noise')
    audio.data = noise_reduction_filter(audio, std_threshold)
    print('Passing High Freq')
    audio.data = high_pass_filter(audio, bottom_cutoff_freq, order=8)
    # print('Pass Low Freq')
    # audio.data = low_pass_filter(audio, top_cutoff_freq, order=8)
    # print('Reducing Noise')
    # audio.data = noise_reduction_filter(audio)
    print('Normalizing')
    audio.data = normalize(audio, normalize_percentage)
    print('Down Sampling')
    audio.data = downsample(audio, new_sample_rate)
    audio.sample_rate = new_sample_rate


    # Create the new filename
    original_path = Path(filepath)
    new_filename = original_path.stem + export_tag + original_path.suffix
    new_filepath = f'{filepath_save}/{new_filename}'


    # Save the filtered audio to the new file
    save_to_wav(audio.data, audio.sample_rate, audio.num_channels, new_filepath)



