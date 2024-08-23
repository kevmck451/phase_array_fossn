

import numpy as np

# Function to Normalize Data
def normalize(data, percentage=100, multiCh=True):

    def norm(data):
        max_value = np.max(np.abs(data))
        if max_value == 0:
            raise Exception('Max Value is Zero')

        data = np.nan_to_num(data)

        return data / (max_value * (percentage / 100.0))

    normalized_data = np.zeros_like(data)

    if not multiCh:
        normalized_data = norm(data)

    else:
        for i in range(data.shape[0]):
            normalized_data[i, :] = norm(data[i, :])

    return normalized_data


