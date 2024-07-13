

from Filters.audio import Audio
from Actions.save_to_wav import save_to_wav

import noisereduce as nr
from pathlib import Path
import numpy as np


def noise_reduction_filter(audio_object):

    reduced_noise_data = np.zeros_like(audio_object.data)
    for channel in range(audio_object.data.shape[0]):
        reduced_noise_data[channel, :] = nr.reduce_noise(
            y=audio_object.data[channel, :],
            sr=audio_object.sample_rate,
            stationary=True,
            # freq_mask_smooth_hz=1000,
            # time_mask_smooth_ms=200,
            use_tqdm=True,
            n_jobs = -1
        )

    reduced_noise_data = np.clip(reduced_noise_data, -1.0, 1.0)

    return reduced_noise_data


if __name__ == '__main__':

    # filepath = '/Users/KevMcK/Dropbox/2 Work/1 Optics Lab/2 FOSSN/Data/Tests/5_outdoor_testing/07-12-2024_02-49-21_chunk_1.wav'
    # audio = Audio(filepath=filepath, num_channels=48)

    filepath = '/Users/KevMcK/Dropbox/2 Work/1 Optics Lab/1 Acoustic/Data/Angel_Mount_Data/2 Flights/A6_Flight_2.wav'
    audio = Audio(filepath=filepath, num_channels=4)

    print(audio)

    filtered_data = noise_reduction_filter(audio)

    print(f'Max: {np.max(filtered_data)}')
    print(f'Min: {np.min(filtered_data)}')

    # Ensure the filtered data shape matches the original
    assert filtered_data.shape == audio.data.shape, "Filtered data shape does not match original data shape"

    # Create the new filename with "_HPF" suffix
    original_path = Path(filepath)
    new_filename = original_path.stem + "_NR2" + original_path.suffix
    new_filepath = str(original_path.parent / new_filename)

    # Save the filtered audio to the new file
    save_to_wav(filtered_data, audio.sample_rate, audio.num_channels, new_filepath)
