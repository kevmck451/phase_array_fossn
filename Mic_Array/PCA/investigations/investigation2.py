import os
from Filters.audio import Audio
import numpy as np
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt
from scipy.signal import stft
from tqdm import tqdm
import matplotlib.cm as cm

base_path = '/Users/KevMcK/Dropbox/2 Work/1 Optics Lab/1 Acoustic/Data/Isolated Samples'
# base_path = '/Users/KevMcK/Dropbox/2 Work/1 Optics Lab/1 Acoustic/Data/Isolated Samples/Ambience'

# categories = ['Angel', 'Angel Wind', 'Diesel', 'Gas', 'Hex', 'Hex Wind', 'Penguin']
categories = ['Angel', 'Angel Wind', 'Hex', 'Hex Wind', 'Penguin']
# categories = ['Diesel', 'Gas']
# c ategories = ['Beach', 'City Center', 'Forest', 'Park']
num_channels = 1
nperseg = 16384
num_pca_components = 2  # Reduced to 2 since we're only plotting the first two components

def load_and_preprocess(filepath):
    audio = Audio(filepath=filepath, num_channels=num_channels)
    _, _, stft_matrix = stft(audio.data.T, nperseg=nperseg, axis=0)
    num_time_bins = stft_matrix.shape[0]
    num_freq_bins = stft_matrix.shape[1]
    feature_matrix = np.abs(stft_matrix).reshape(num_time_bins, num_freq_bins * num_channels)
    return feature_matrix

def apply_pca(feature_matrix):
    pca = PCA(n_components=num_pca_components)
    principal_components = pca.fit_transform(feature_matrix)
    return pca, principal_components

category_pca_results = {}
global_min_x, global_max_x, global_min_y, global_max_y = float('inf'), float('-inf'), float('inf'), float('-inf')

# Collect all PCA results with progress tracking using tqdm
for category in tqdm(categories, desc="Processing Categories"):
    category_path = os.path.join(base_path, category)
    principal_components_list = []
    sound_files = [f for f in os.listdir(category_path) if f.endswith('.wav')]
    for sound_file in tqdm(sound_files, desc=f"Processing {category}", leave=False):
        filepath = os.path.join(category_path, sound_file)
        feature_matrix = load_and_preprocess(filepath)
        pca, principal_components = apply_pca(feature_matrix)
        principal_components_list.append((sound_file, principal_components))
        global_min_x = min(global_min_x, np.min(principal_components[:, 0]))
        global_max_x = max(global_max_x, np.max(principal_components[:, 0]))
        global_min_y = min(global_min_y, np.min(principal_components[:, 1]))
        global_max_y = max(global_max_y, np.max(principal_components[:, 1]))
    if principal_components_list:
        category_pca_results[category] = principal_components_list

# Plot PCA results for all categories at the end
num_categories = len(category_pca_results)
fig, axes = plt.subplots(1, num_categories, figsize=(24, 12))

for i, (category, principal_components_list) in enumerate(category_pca_results.items()):
    colormap = cm.get_cmap('tab20', len(principal_components_list))
    for j, (sound_file, principal_components) in enumerate(principal_components_list):
        axes[i].scatter(principal_components[:, 0], principal_components[:, 1], color=colormap(j), alpha=0.5)
    axes[i].set_xlabel('Principal Component 1')
    axes[i].set_ylabel('Principal Component 2')
    axes[i].set_title(f'PCA of {category}')
    axes[i].set_xlim(global_min_x, global_max_x)
    axes[i].set_ylim(global_min_y, global_max_y)

plt.tight_layout()
plt.show()
