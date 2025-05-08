

from Mic_Array.Audio_Stream.AudioStreamSimulator import AudioStreamSimulator
from Filters.audio import Audio



from sklearn.decomposition import PCA
from scipy.signal import stft
import numpy as np


from queue import Queue
import time


class PCA_Calculator:
    def __init__(self,
                 nperseg=4096,
                 num_components=3,
                 threshold_multiplier=10):
        self.nperseg = nperseg
        self.num_components = num_components
        self.threshold_multiplier = threshold_multiplier
        self.queue = Queue()

    def process_chunk(self, chunk):
        data = []

        for channel in chunk:
            frequencies, times, stft_matrix = stft(channel.T, nperseg=self.nperseg, axis=0)
            num_time_bins = stft_matrix.shape[0]
            num_freq_bins = stft_matrix.shape[1]
            feature_matrix = np.abs(stft_matrix).reshape(num_time_bins, num_freq_bins)

            pca = PCA(n_components=self.num_components)
            principal_components = pca.fit_transform(feature_matrix)

            data.append(principal_components.T)

        data_array = np.array(data)
        self.queue.put(data_array)



if __name__ == '__main__':
    base_path = '/Users/KevMcK/Dropbox/2 Work/1 Optics Lab/2 FOSSN/Data'
    filename = 'cars_drive_by_150m_BF_(-70, 70)-(0)'
    filepath = f'{base_path}/Tests/18_beamformed/{filename}.wav'
    angles = [-70, -60, -50, -40, -30, -20, -10, 0, 10, 20, 30, 40, 50, 60, 70]
    audio = Audio(filepath=filepath, num_channels=len(angles))
    chunk_size_seconds = 1

    pca_detector = PCA_Calculator()

    stream = AudioStreamSimulator(audio, chunk_size_seconds)
    stream.start_stream()
    while stream.running:
        if not stream.queue.empty():
            print('PROCESSING----------')
            print(f'Audio Stream Queue Size: {stream.queue.qsize()}')
            current_audio_data = stream.queue.get()
            print(f'Current Data Size: {current_audio_data.shape}')
            #-------------------------
            pca_detector.process_chunk(current_audio_data)
            print(f'PCA Queue Size: {pca_detector.queue.qsize()}')
            if not pca_detector.queue.empty():
                current_pca_data = pca_detector.queue.get()
                print(f'PCA Data Type: {type(current_pca_data)}')
                print(f'PCA Data Length: {len(current_pca_data)}')
                print(f'PCA Data Shape at 0: {current_pca_data.get(0).shape}')
            print()
            print('='*40)
            print()
        time.sleep(0.25)







































