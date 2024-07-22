import numpy as np
from scipy.signal import resample

# Function to Down-sample Data
def downsample(audio_object, target_sample_rate=12000):
    current_sample_rate = audio_object.sample_rate
    if target_sample_rate >= current_sample_rate:
        raise ValueError("Target sample rate must be less than current sample rate.")

    def downsample_data(data, current_rate, target_rate):
        num_samples = int(len(data) * target_rate / current_rate)
        return resample(data, num_samples)

    if audio_object.num_channels == 1:
        downsampled_data = downsample_data(audio_object.data, current_sample_rate, target_sample_rate)
    else:
        downsampled_data = np.zeros((audio_object.num_channels, int(audio_object.data.shape[1] * target_sample_rate / current_sample_rate)))
        for i in range(audio_object.num_channels):
            downsampled_data[i, :] = downsample_data(audio_object.data[i, :], current_sample_rate, target_sample_rate)

    return downsampled_data

