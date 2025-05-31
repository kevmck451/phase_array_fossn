



from datetime import datetime
from queue import Queue
import numpy as np
import random
import time
import os


class Detector:
    def __init__(self):

        self.baseline_calculated = False # set outside this class
        self.queue = Queue()
        self.counter = 0 # for simulation

        self.max_value = 25 # this is what sets the bar graphs. This number is 100%
        self.anomaly_threshold = 8

        self.num_channels = None
        self.num_pca_components = None
        self.num_samples = None

        self.baseline_means = None
        self.baseline_stds = None

        self.bias_scale_factor = 0.99
        self.bias_margin = 0.5
        self.bias_theta_ratio = 0.7

        self.edge_width = 4
        self.suppression_factor = 0.5

    def calculate_baseline(self, pca_data):
        '''
        pca_data is a numpy array where the first axis is direction from most negative to positive
        and the other is a numpy array of pca components from beamformed data
        pca_data.shape = (num_channels, num_pca_components, num_samples)
        '''
        # print(f'PCA_DATA: {type(pca_data)}\t|\t{pca_data.shape}')
        # PCA_DATA: <class 'numpy.ndarray'>	|	(19, 3, 2049)

        # If this is the first time, initialize the baseline means and stds
        if self.baseline_means is None or self.baseline_stds is None:
            self.baseline_means = np.mean(pca_data, axis=2)
            self.baseline_stds = np.std(pca_data, axis=2)
        else:
            # Update the baseline with a moving average
            current_mean = np.mean(pca_data, axis=2)
            current_std = np.std(pca_data, axis=2)

            # Moving average update for the mean and std (adjust weight if needed)
            self.baseline_means = 0.8 * self.baseline_means + 0.2 * current_mean
            self.baseline_stds = 0.8 * self.baseline_stds + 0.2 * current_std

    def detect_anomalies(self, pca_data):
        self.num_channels, self.num_pca_components, self.num_samples = pca_data.shape

        if self.baseline_means is None or self.baseline_stds is None:
            self.calculate_baseline(pca_data)
            return

        if not self.baseline_calculated:
            self.calculate_baseline(pca_data)
            return

        else:
            anomalies_list = []

            # Loop through each channel and detect anomalies based on PCA data
            for ch in range(self.num_channels):
                # Get current PCA data for the channel
                channel_data = pca_data[ch]
                # Ensure the baseline mean and std are correctly shaped
                baseline_mean = self.baseline_means[ch].reshape(self.num_pca_components, 1)
                baseline_std = self.baseline_stds[ch].reshape(self.num_pca_components, 1)

                # Compute the deviation from the baseline
                deviations = np.abs(channel_data - baseline_mean) > (baseline_std * self.anomaly_threshold)

                # Count the number of anomalies (deviations exceeding threshold)
                num_anomalies = np.sum(deviations)

                # Append the result to the anomalies list
                anomalies_list.append(num_anomalies)

            # Convert to numpy array for consistency
            anomalies_list = np.array(anomalies_list)

            # Ensure the list has the correct number of channels
            assert len(anomalies_list) == self.num_channels

            # Add the anomaly results to the queue for further processing

            # Remove Bias like Wind
            anomalies_list = self.remove_bias(anomalies_list)
            # Suppress Edges which activate easily
            anomalies_list = self.suppress_edges(anomalies_list)

            self.queue.put(anomalies_list)

    def remove_bias(self, anomalies):
        # print('removing bias like wind')

        mean_val = sum(anomalies) / len(anomalies)
        if mean_val == 0:
            return anomalies  # avoid division by zero

        threshold = self.bias_margin * abs(mean_val)

        # Count how many values are within mean ± threshold
        count_within_margin = sum(abs(a - mean_val) <= threshold for a in anomalies)
        ratio_within = count_within_margin / len(anomalies)

        if ratio_within >= self.bias_theta_ratio:
            bias = mean_val * self.bias_scale_factor
            # print(f"Mean: {mean_val:.2f}, Threshold: {threshold:.2f}, Within Margin: {count_within_margin}/{len(anomalies)}, Bias: {bias:.2f}")
            anomalies = [max(0, int(round(a - bias))) for a in anomalies]

        return anomalies

    def suppress_edges(self, anomalies):
        length = len(anomalies)
        new_anomalies = anomalies[:]

        for i in range(self.edge_width):
            scale = self.suppression_factor + (1 - self.suppression_factor) * (i / (self.edge_width - 1))
            new_anomalies[i] = int(round(new_anomalies[i] * scale))
            new_anomalies[length - 1 - i] = int(round(new_anomalies[length - 1 - i] * scale))

        return new_anomalies

    def detect_anomalies_simulation(self, pca_data):

        if not self.baseline_calculated:
            self.calculate_baseline(pca_data)

        else:
            # print(self.baseline_means)
            anomalies_list = self.generate_random_data(19)
            anomalies_list = np.array(anomalies_list)
            self.queue.put(anomalies_list)

    # Generate random values below 30% of the max, with spikes every 10th time
    def generate_random_data(self, size):
        self.counter += 1
        if self.counter % 10 == 0:
            # Every 10th time, allow full range random values
            return [round(random.uniform(0, self.max_value), 1) for _ in range(size)]
        else:
            # Keep values below 30% of the max value
            max_allowed = self.max_value * 0.3
            return [round(random.uniform(0, max_allowed), 1) for _ in range(size)]


if __name__ == '__main__':
    pass