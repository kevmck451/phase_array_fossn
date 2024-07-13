
from Filters.audio import Audio
from Actions.save_to_wav import save_to_wav


from scipy.signal import butter, lfilter
from pathlib import Path
import numpy as np


def low_pass_filter(audio_object, cutoff_freq, order=5):
    '''
    Order 1-2: Gentle roll-off. Suitable for applications where a gradual transition is acceptable.
    Order 3-4: Moderate roll-off. Offers a balance between roll-off steepness and computational complexity.
    Order 5-6: Steeper roll-off. Provides better separation between the passband and stopband frequencies.
    Order 7-10: Very steep roll-off. Useful for applications requiring precise frequency separation, but can be more computationally intensive and may introduce more phase distortion.
    '''

    nyquist = 0.5 * audio_object.sample_rate
    normal_cutoff = cutoff_freq / nyquist

    def low_pass(data, cutoff_frequency, order):
        b, a = butter(order, cutoff_frequency, btype='low', analog=False)
        filtered_data = lfilter(b, a, data)
        # Normalize the filtered data to stay within the range [-1, 1]
        filtered_data = np.clip(filtered_data, -1.0, 1.0)
        return filtered_data

    # Apply the high-pass filter to each channel
    filtered_data = np.zeros_like(audio_object.data)
    for i in range(audio_object.data.shape[0]):
        filtered_data[i, :] = low_pass(audio_object.data[i, :], normal_cutoff, order)

    return filtered_data


if __name__ == '__main__':

    filepath = '/Users/KevMcK/Dropbox/2 Work/1 Optics Lab/2 FOSSN/Data/Tests/5_outdoor_testing/07-12-2024_02-49-21_chunk_1.wav'

    audio = Audio(filepath=filepath, num_channels=48)
    print(audio)

    cutoff_frequency = 1000  # Set your desired cutoff frequency (in Hz)

    filtered_data = low_pass_filter(audio, cutoff_frequency)

    print(f'Max: {np.max(filtered_data)}')
    print(f'Min: {np.min(filtered_data)}')

    # Ensure the filtered data shape matches the original
    assert filtered_data.shape == audio.data.shape, "Filtered data shape does not match original data shape"

    # Create the new filename with "_HPF" suffix
    original_path = Path(filepath)
    new_filename = original_path.stem + "_HPF" + original_path.suffix
    new_filepath = str(original_path.parent / new_filename)

    # Save the filtered audio to the new file
    save_to_wav(filtered_data, audio.sample_rate, audio.num_channels, new_filepath)