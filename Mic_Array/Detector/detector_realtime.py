

from Mic_Array.AudioStreamSimulator import AudioStreamSimulator
from Filters.audio import Audio



from sklearn.decomposition import PCA
from scipy.signal import stft
import numpy as np


from queue import Queue
import time


class Detector:
    def __init__(self, threshold_multiplier=10, baseline_calculations=10):
        self.threshold_multiplier = threshold_multiplier
        self.baseline_calculations = baseline_calculations
        self.baseline_means = {}
        self.baseline_stds = {}
        self.queue = Queue()

        self.baseline_calculated = False
        self.baseline_iterations = 10

    def calculate_baseline(self, pca_data):
        '''
        pca_data is a dictionary where the keys are signed ints
        and the values are pca components from beamformed data

        '''

        print(f'PCA Data: {pca_data.get(0).shape}')

        self.baseline_means = {}
        self.baseline_stds = {}

        for angle, pcs in pca_data.items():
            baseline_data = pcs[:self.baseline_calculations]
            self.baseline_means[angle] = np.mean(baseline_data, axis=0)
            self.baseline_stds[angle] = np.std(baseline_data, axis=0)

        self.baseline_calculated = True

    def detect_anomalies(self, pca_data):
        anomalies_list = {}

        if not self.baseline_calculated:
            self.calculate_baseline(pca_data)

        else:
            for angle, pcs in pca_data.items():
                mean = self.baseline_means.get(angle)
                std = self.baseline_stds.get(angle)

                # print(f'DETECTOR MEAN & STD: {mean}, {std}')
                if mean is not None and std is not None:
                    threshold_radius = np.linalg.norm(self.threshold_multiplier * std, axis=0)
                    distances = np.linalg.norm(pcs - mean, axis=1)
                    anomalies = distances > threshold_radius

                    anomaly_count = np.sum(anomalies)
                    anomalies_list[angle] = anomaly_count

            self.queue.put(anomalies_list)




if __name__ == '__main__':
    pass