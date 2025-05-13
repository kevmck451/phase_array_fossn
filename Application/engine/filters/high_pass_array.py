

import Mic_Array.array_config as array_config


from scipy.signal import butter, lfilter
import numpy as np

def high_pass_filter(data, cutoff_freq, multiCh=True, order=5):

    '''
    Order 1-2: Gentle roll-off. Suitable for applications where a gradual transition is acceptable.
    Order 3-4: Moderate roll-off. Offers a balance between roll-off steepness and computational complexity.
    Order 5-6: Steeper roll-off. Provides better separation between the passband and stopband frequencies.
    Order 7-10: Very steep roll-off. Useful for applications requiring precise frequency separation, but can be more computationally intensive and may introduce more phase distortion.
    '''

    nyquist = 0.5 * array_config.sample_rate
    normal_cutoff = cutoff_freq / nyquist

    def high_pass(data, cutoff_frequency, order):
        b, a = butter(order, cutoff_frequency, btype='high', analog=False)
        filtered_data = lfilter(b, a, data)
        # Normalize the filtered data to stay within the range [-1, 1]
        # filtered_data = np.clip(filtered_data, -1.0, 1.0)
        return filtered_data

    # Apply the high-pass filter to each channel
    filtered_data = np.zeros_like(data)

    if not multiCh:
        filtered_data = high_pass(data, normal_cutoff, order)

    else:
        for i in range(data.shape[0]):
            filtered_data[i, :] = high_pass(data[i, :], normal_cutoff, order)

    return filtered_data

