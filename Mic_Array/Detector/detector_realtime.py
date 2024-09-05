


import numpy as np


from queue import Queue
import random
import time


class Detector:
    def __init__(self):
        self.baseline_calculated = False # set outside this class
        self.baseline_calibration_time = 5 # used outside this class
        self.queue = Queue()
        self.counter = 0 # for simulation

        self.max_value = 150 # this is what sets the bar graphs. This number is 100%

        self.num_channels = None
        self.num_pca_components = None
        self.num_samples = None

    def calculate_baseline(self, pca_data):
            '''
            pca_data is a numpy array where the first axis is direction from most negative to positive
            and the other is a numpy array of pca components from beamformed data
            pca_data.shape = (num_channels, num_pca_components, num_samples)
            '''
            # print(f'PCA_DATA: {type(pca_data)}\t|\t{pca_data.shape}')
            # PCA_DATA: <class 'numpy.ndarray'>	|	(19, 3, 2049)

            self.num_channels, self.num_pca_components, self.num_samples = pca_data.shape


    def detect_anomalies(self, pca_data):

        if not self.baseline_calculated:
            self.calculate_baseline(pca_data)

        else:
            anomalies_list = []


            anomalies_list = np.array(anomalies_list)
            assert len(anomalies_list) == self.num_channels
            self.queue.put(anomalies_list)


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