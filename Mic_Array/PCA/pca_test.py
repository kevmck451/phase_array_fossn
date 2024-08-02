from Filters.audio import Audio
import numpy as np
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt
from scipy.signal import stft

base_path = '/Users/KevMcK/Dropbox/2 Work/1 Optics Lab/2 FOSSN/Data'

filename = 'angel_sweep_BF_(-70, 70)-(0)_Pro_2'
# filename = 'angel_sensitivity_BF_(-70, 70)-(0)_Pro_1'

filepath = f'{base_path}/Tests/16_beamformed/{filename}.wav'

num_channels = 15

audio = Audio(filepath=filepath, num_channels=num_channels)
print("Audio data shape:", audio.data.shape)

# Feature extraction using STFT
nperseg = 8192 # 256
frequencies, times, stft_matrix = stft(audio.data.T, nperseg=nperseg, axis=0)
print("STFT matrix shape:", stft_matrix.shape)

# Reshape the STFT matrix to create the feature matrix
num_time_bins = stft_matrix.shape[0]
num_freq_bins = stft_matrix.shape[1]
num_channels = stft_matrix.shape[2]

# Correct reshaping dimensions
feature_matrix = np.abs(stft_matrix).reshape(num_time_bins, num_freq_bins * num_channels)
print("Feature matrix shape:", feature_matrix.shape)

# Apply PCA
pca = PCA(n_components=50)  # Adjust number of components as needed
principal_components = pca.fit_transform(feature_matrix)

# Plot the variance explained by each principal component
plt.figure()
plt.plot(np.cumsum(pca.explained_variance_ratio_))
plt.xlabel('Number of Components')
plt.ylabel('Variance Explained')
plt.title('PCA Variance Explained')
plt.show()

# Plot the first two principal components
plt.figure()
plt.scatter(principal_components[:, 0], principal_components[:, 1])
plt.xlabel('Principal Component 1')
plt.ylabel('Principal Component 2')
plt.title('Principal Component Analysis')
plt.show()


plt.figure()
plt.scatter(principal_components[:, 2], principal_components[:, 3])
plt.xlabel('Principal Component 3')
plt.ylabel('Principal Component 4')
plt.title('Principal Component Analysis')
plt.show()
