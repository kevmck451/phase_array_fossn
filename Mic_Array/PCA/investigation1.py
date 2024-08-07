from Filters.audio import Audio
import numpy as np
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt
from scipy.signal import stft

base_path = '/Users/KevMcK/Dropbox/2 Work/1 Optics Lab/2 FOSSN/Data'

# filename = 'angel_far_long'
# filename = 'diesel_idle_1_4'
# filename = 'diesel_tractor_9_1'
filename = 'hex_hover_thick_LONG'

filepath = f'{base_path}/Sounds/{filename}.wav'

num_channels = 1

audio = Audio(filepath=filepath, num_channels=num_channels)
print("Audio data shape:", audio.data.shape)

# Feature extraction using STFT
nperseg = 16384 # 256
frequencies, times, stft_matrix = stft(audio.data.T, nperseg=nperseg, axis=0)
print("STFT matrix shape:", stft_matrix.shape)

# Reshape the STFT matrix to create the feature matrix
num_time_bins = stft_matrix.shape[0]
num_freq_bins = stft_matrix.shape[1]
# num_channels = stft_matrix.shape[2]

# Correct reshaping dimensions
feature_matrix = np.abs(stft_matrix).reshape(num_time_bins, num_freq_bins * num_channels)
print("Feature matrix shape:", feature_matrix.shape)

# Apply PCA
pca = PCA(n_components=50)  # Adjust number of components as needed
principal_components = pca.fit_transform(feature_matrix)

# Calculate cumulative variance explained
cumulative_variance_explained = np.cumsum(pca.explained_variance_ratio_)

# Find the number of components that cover most of the data
threshold = 0.95  # Adjust as needed for "most of the data"
num_components_to_cover_variance = np.argmax(cumulative_variance_explained >= threshold) + 1

# Plot the variance explained by each principal component
plt.figure()
plt.plot(cumulative_variance_explained, label='Variance Explained')
plt.axvline(x=num_components_to_cover_variance, color='r', linestyle='--', label=f'{num_components_to_cover_variance} Components')
plt.xlabel('Number of Components')
plt.ylabel('Variance Explained')
plt.title('PCA Variance Explained')
plt.legend()
plt.show()

# Plot the first two principal components
plt.figure()
plt.scatter(principal_components[:, 0], principal_components[:, 1])
plt.xlabel('Principal Component 1')
plt.ylabel('Principal Component 2')
plt.title('Principal Component Analysis')
plt.show()


plt.figure()
plt.scatter(principal_components[:, 0], principal_components[:, 2])
plt.xlabel('Principal Component 3')
plt.ylabel('Principal Component 4')
plt.title('Principal Component Analysis')
plt.show()


