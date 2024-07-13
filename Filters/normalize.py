

import numpy as np

# Function to Normalize Data
def normalize(audio_object, percentage=100):

    def norm(data):
        max_value = np.max(np.abs(data))
        if max_value == 0:
            raise Exception('Max Value is Zero')

        data = np.nan_to_num(data)

        return data / (max_value * (percentage / 100.0))

    normalized_data = np.zeros_like(audio_object.data)
    for i in range(audio_object.data.shape[0]):
        normalized_data[i, :] = norm(audio_object.data[i, :])

    return normalized_data