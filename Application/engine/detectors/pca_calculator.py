


from sklearn.decomposition import PCA
from scipy.signal import stft
from queue import Queue
import numpy as np
import warnings

class PCA_Calculator:
    def __init__(self, nperseg=4096, num_components=3):
        self.nperseg = nperseg
        self.num_components = num_components
        self.stft_shape = None
        self.queue = Queue()

    def process_chunk(self, chunk):

        data = []

        with warnings.catch_warnings():
            warnings.simplefilter("ignore", category=UserWarning)

            for channel in chunk:
                # self.nperseg = channel.shape[-1]
                frequencies, times, stft_matrix = stft(channel.T, nperseg=self.nperseg, axis=0)
                num_time_bins = stft_matrix.shape[0]
                num_freq_bins = stft_matrix.shape[1]
                feature_matrix = np.abs(stft_matrix).reshape(num_time_bins, num_freq_bins)
                self.stft_shape = stft_matrix.shape

                pca = PCA(n_components=self.num_components)
                principal_components = pca.fit_transform(feature_matrix)

                data.append(principal_components.T)

        data_array = np.array(data)
        self.queue.put(data_array)





































