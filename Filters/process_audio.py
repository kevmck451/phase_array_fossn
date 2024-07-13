
from Filters.noise_reduction import noise_reduction_filter
from Filters.high_pass import high_pass_filter
from Filters.low_pass import low_pass_filter
from Filters.normalize import normalize
from Actions.save_to_wav import save_to_wav
from Filters.audio import Audio

from pathlib import Path
import numpy as np

if __name__ == '__main__':

    # filepath = '/Users/KevMcK/Dropbox/2 Work/1 Optics Lab/1 Acoustic/Data/Angel_Mount_Data/2 Flights/A6_Flight_2.wav'
    filepath = '/Users/KevMcK/Dropbox/2 Work/1 Optics Lab/1 Acoustic/Data/Angel_Mount_Data/2 Flights/A6_Flight_3.wav'
    audio = Audio(filepath=filepath, num_channels=4)

    # filepath = '/Users/KevMcK/Dropbox/2 Work/1 Optics Lab/2 FOSSN/Data/Tests/5_outdoor_testing/07-12-2024_02-49-21_chunk_1.wav'
    # audio = Audio(filepath=filepath, num_channels=48)


    shape_og = audio.data.shape
    print(audio)

    # Noise Reduction
    audio.data = noise_reduction_filter(audio)

    # High Pass Filter
    bottom_cutoff_freq = 500
    audio.data = high_pass_filter(audio, bottom_cutoff_freq)

    # Low Pass Filter
    top_cutoff_freq = 2000
    audio.data = low_pass_filter(audio, top_cutoff_freq)

    # Noise Reduction
    # audio.data = noise_reduction_filter(audio)

    # Snip Ends which are garbage from NR
    audio.data = audio.data[:, 50000:-50000]

    # Normalize
    audio.data = normalize(audio)




    print(f'Max: {np.max(audio.data)}')
    print(f'Min: {np.min(audio.data)}')

    # Ensure the filtered data shape matches the original
    # assert audio.data.shape == shape_og, "Filtered data shape does not match original data shape"

    # Create the new filename with "_HPF" suffix
    original_path = Path(filepath)
    new_filename = original_path.stem + "_processed20" + original_path.suffix
    new_filepath = str(original_path.parent / new_filename)

    # Save the filtered audio to the new file
    save_to_wav(audio.data, audio.sample_rate, audio.num_channels, new_filepath)



