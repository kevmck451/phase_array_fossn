from Filters.audio import Audio
import numpy as np
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt
from scipy.signal import stft
import matplotlib.animation as animation
from matplotlib.animation import FFMpegWriter
from tqdm import tqdm
import h5py

base_path = '/Users/KevMcK/Dropbox/2 Work/1 Optics Lab/2 FOSSN/Data'
filename = '07-22-2024_01-36-01_chunk_1_BF_(-40, 40)-0'
filepath = f'{base_path}/Tests/13_beamformed/old3/{filename}.wav'
filepath_save = f'{base_path}/PCA/testing1/{filename}_PCA4.mp4'

num_channels = 9
chunk_size_seconds = 1  # Desired chunk size in seconds
nperseg = 2048  # Adjust as needed
angles = [-40, -30, -20, -10, 0, 10, 20, 30, 40]

audio = Audio(filepath=filepath, num_channels=num_channels)
chunk_size = int(chunk_size_seconds * audio.sample_rate)

# Function to process a chunk and apply PCA for a specific channel
def process_chunk(chunk, nperseg, pca_components=15):
    frequencies, times, stft_matrix = stft(chunk.T, nperseg=nperseg, axis=0)
    num_time_bins = stft_matrix.shape[0]
    num_freq_bins = stft_matrix.shape[1]
    feature_matrix = np.abs(stft_matrix).reshape(num_time_bins, num_freq_bins)

    pca = PCA(n_components=pca_components)
    principal_components = pca.fit_transform(feature_matrix)

    return principal_components

# Check if the data file exists, otherwise process and save the data
data_save_path = f'{base_path}/PCA/data/{filename}_{chunk_size_seconds}_{nperseg}_data.h5'
try:
    with h5py.File(data_save_path, 'r') as f:
        num_chunks = f.attrs['num_chunks']
        principal_components_list = [
            [f[f'channel_{c}_chunk_{i}'][:] for i in range(num_chunks)]
            for c in range(num_channels)
        ]
        print("Data loaded from file.")
except (OSError, KeyError):
    print("Processing data...")
    num_chunks = audio.data.shape[1] // chunk_size
    principal_components_list = [[] for _ in range(num_channels)]

    with h5py.File(data_save_path, 'w') as f:
        for c in range(num_channels):
            for i in tqdm(range(num_chunks), desc=f"Processing Chunks for Channel {c}"):
                chunk = audio.data[c, int(i * chunk_size):int((i + 1) * chunk_size)]
                principal_components = process_chunk(chunk, nperseg)
                principal_components_list[c].append(principal_components)
                f.create_dataset(f'channel_{c}_chunk_{i}', data=principal_components)
        f.attrs['nperseg'] = nperseg
        f.attrs['pca_components'] = 10
        f.attrs['chunk_size_seconds'] = chunk_size_seconds
        f.attrs['num_chunks'] = num_chunks

# Set up the figure and axis for the animation
fig, axes = plt.subplots(1, num_channels, figsize=(24, 5))
sc_list = []

# Initialize scatter plots for each channel
for i, ax in enumerate(axes.flat):
    sc = ax.scatter([], [])
    ax.set_xlim(-1, 1)
    ax.set_ylim(-1, 1)
    ax.set_xlabel('PC 1')
    ax.set_ylabel('PC 2')
    ax.set_title(f'Ch {angles[i]}°')
    sc_list.append(sc)

# Assign colors based on the index of data points
colors = plt.cm.viridis(np.linspace(0, 1, principal_components_list[0][0].shape[0]))

# Animation update function
def update(frame):
    for i, sc in enumerate(sc_list):
        sc.set_offsets(principal_components_list[i][frame][:, :2])
        sc.set_color(colors)
    return sc_list

# Create the animation
fps = 1 / chunk_size_seconds
ani = animation.FuncAnimation(fig, update, frames=num_chunks, interval=chunk_size_seconds * 1000, blit=True)

# Show the animation
# plt.show()

# Save the animation to a video file
writer = FFMpegWriter(fps=fps, metadata=dict(artist='Me'), bitrate=1800)
ani.save(filepath_save, writer=writer)
