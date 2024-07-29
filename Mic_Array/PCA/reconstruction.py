from Filters.audio import Audio
from Filters.save_to_wav import save_to_wav


import numpy as np
from sklearn.decomposition import PCA

# Step 1: Data Collection
# data = np.random.rand(48, 1000)  # 48 channels, 1000 samples


base_path = '/Users/KevMcK/Dropbox/2 Work/1 Optics Lab/2 FOSSN/Data'
filename = '07-16-2024_03-25-22_chunk_1_cropped'
filepath = f'{base_path}/Tests/9_outdoor_testing/{filename}.wav'
num_channels = 48

audio = Audio(filepath=filepath, num_channels=num_channels)

# Step 2: Transpose for PCA
data_transposed = audio.data.T  # Shape now is (samples, channels)

# Step 3: Apply PCA
pca = PCA(n_components=10)  # Reduce to 10 principal components
transformed_data = pca.fit_transform(data_transposed)

# Step 4: Reconstruct the Signal
reconstructed_data_transposed = pca.inverse_transform(transformed_data)

# Transpose back to original orientation (channels as rows)
reconstructed_data = reconstructed_data_transposed.T

# Check reconstruction error
reconstruction_error = np.mean((audio.data - reconstructed_data) ** 2)
print(f'Reconstruction Error: {reconstruction_error}')

audio.data = reconstructed_data
filepath_save = f'{base_path}/PCA/testing2/{filename}_PCA_recon2.wav'
save_to_wav(audio.data, audio.sample_rate, audio.num_channels, filepath_save)
