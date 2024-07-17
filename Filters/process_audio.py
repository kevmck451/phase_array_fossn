
from Filters.noise_reduction import noise_reduction_filter
from Filters.high_pass import high_pass_filter
from Filters.low_pass import low_pass_filter
from Filters.normalize import normalize
from Filters.save_to_wav import save_to_wav
from Filters.audio import Audio

from pathlib import Path
import numpy as np

if __name__ == '__main__':
    base_path = '/Users/KevMcK/Dropbox/2 Work/1 Optics Lab/2 FOSSN/Data'

    # filepath = '/Users/KevMcK/Dropbox/2 Work/1 Optics Lab/2 FOSSN/Data/Tests/5_outdoor_testing/07-12-2024_02-49-21_chunk_1.wav'
    # filepath = '/Users/KevMcK/Dropbox/2 Work/1 Optics Lab/2 FOSSN/Data/Tests/7_hallway_tone/07-15-2024_03-25-28_chunk_1.wav'

    # filepath = '/Users/KevMcK/Dropbox/2 Work/1 Optics Lab/2 FOSSN/Data/Tests/7_hallway_tone/07-15-2024_03-33-35_chunk_1.wav'
    # audio = Audio(filepath=filepath, num_channels=48)

    filepath = '/Users/KevMcK/Dropbox/2 Work/1 Optics Lab/2 FOSSN/Data/Tests/10_beamformed/07-16-2024_03-25-22_chunk_1_BF1_45-0.wav'
    audio = Audio(filepath=filepath, num_channels=1)

    export_tag = '_pr1'
    filepath_save = f'{base_path}/Tests/10_beamformed'

    shape_og = audio.data.shape
    # print(audio)

    # Noise Reduction
    print('Reducing Noise')
    std_threshold = 0.5
    audio.data = noise_reduction_filter(audio, std_threshold)

    # High Pass Filter
    print('Passing High Freq')
    bottom_cutoff_freq = 500
    audio.data = high_pass_filter(audio, bottom_cutoff_freq, order=8)

    # Low Pass Filter
    print('Pass Low Freq')
    top_cutoff_freq = 3000
    audio.data = low_pass_filter(audio, top_cutoff_freq, order=8)

    # Noise Reduction
    # print('Reducing Noise')
    # audio.data = noise_reduction_filter(audio)

    # Snip Ends which are garbage from NR
    print('Truncating Edges')
    if audio.num_channels == 1: audio.data = audio.data[50000:-50000]
    else: audio.data = audio.data[:, 50000:-50000]

    # Normalize
    print('Normalizing')
    audio.data = normalize(audio)

    print(f'Max: {np.max(audio.data)}')
    print(f'Min: {np.min(audio.data)}')

    # Create the new filename
    original_path = Path(filepath)
    new_filename = original_path.stem + export_tag + original_path.suffix
    new_filepath = f'{filepath_save}/{new_filename}'


    # Save the filtered audio to the new file
    save_to_wav(audio.data, audio.sample_rate, audio.num_channels, new_filepath)



