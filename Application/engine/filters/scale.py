

import numpy as np

# Function to Scale Data
def scale(data, scale_factor=100.0, multiCh=True):

    def scale(data):
        return data * scale_factor

    scaled_data = np.zeros_like(data)

    if not multiCh:
        scaled_data = scale(data)

    else:
        for i in range(data.shape[0]):
            scaled_data[i, :] = scale(data[i, :])

    return scaled_data


