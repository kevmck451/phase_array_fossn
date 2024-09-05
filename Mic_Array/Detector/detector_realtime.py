

from Mic_Array.AudioStreamSimulator import AudioStreamSimulator
from Filters.audio import Audio



from sklearn.decomposition import PCA
from scipy.signal import stft
import numpy as np


from queue import Queue
import random
import time


class Detector:
    def __init__(self, threshold_multiplier=10, baseline_calculations=10):
        self.threshold_multiplier = threshold_multiplier
        self.baseline_calculations = baseline_calculations
        self.baseline_means = {}
        self.baseline_stds = {}
        self.queue = Queue()

        self.baseline_calculated = False
        self.baseline_calibration_time = 10

        self.max_value = 150
        self.counter = 0

    def calculate_baseline(self, pca_data):
        '''
        pca_data is a numpy array where the first axis is direction from most negative to positive
        and the other is a numpy array of pca components from beamformed data

        '''

        self.baseline_means = self.generate_random_data(19)
        self.baseline_stds = self.generate_random_data(19)

        print(f'PCA_DATA: {type(pca_data)}\t|\t{pca_data.shape}')

        # for angle, pcs in pca_data.items():
        #     baseline_data = pcs[:self.baseline_calculations]
        #     self.baseline_means[angle] = np.mean(baseline_data, axis=0)
        #     self.baseline_stds[angle] = np.std(baseline_data, axis=0)

    def detect_anomalies(self, pca_data):

        if not self.baseline_calculated:
            self.calculate_baseline(pca_data)

        else:
            print(self.baseline_means)
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