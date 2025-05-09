
import Mic_Array.array_config as array_config

import noisereduce as nr
import numpy as np


def noise_reduction_filter(data, std_threshold=1.5, multiCh=True):

    reduced_noise_data = np.zeros_like(data)

    if not multiCh:
        reduced_noise_data = nr.reduce_noise(
            y=data,
            sr=array_config.sample_rate,
            stationary=True,  # stationary noise reduction
            freq_mask_smooth_hz=2000,  # default is 500Hz
            time_mask_smooth_ms=1000,  # default is 50ms
            use_tqdm=True,  # show terminal progress bar
            n_std_thresh_stationary=std_threshold,  # default is 1.5
            n_jobs=-1  # use all available cores
        )
        reduced_noise_data = reduced_noise_data[:, 50:-50]

    else:
        for channel in range(data.shape[0]):
            reduced_noise_data[channel, :] = nr.reduce_noise(
                y=data[channel, :],
                sr=array_config.sample_rate,
                stationary=True, # stationary noise reduction
                freq_mask_smooth_hz=2000, # default is 500Hz
                time_mask_smooth_ms=1000, # default is 50ms
                use_tqdm=True, # show terminal progress bar
                n_std_thresh_stationary = std_threshold, # default is 1.5
                n_jobs = -1 # use all available cores
            )
        reduced_noise_data = reduced_noise_data[:, 50:-50]

    reduced_noise_data = np.clip(reduced_noise_data, -1.0, 1.0)

    return reduced_noise_data



