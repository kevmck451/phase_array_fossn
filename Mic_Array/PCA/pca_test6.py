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
# filename = 'angel_sweep_BF_(-70, 70)-(0)_Pro_1'
filename = 'angel_sensitivity_BF_(-70, 70)-(0)_Pro_1'
# filename = 'diesel_sweep_BF_(-70, 70)-0'
# filepath = f'{base_path}/Tests/13_beamformed/old3/{filename}.wav'
filepath = f'{base_path}/Tests/16_beamformed/{filename}.wav'
filepath_save = f'{base_path}/PCA/testing4/{filename}_PCA_AD_2.mp4'


chunk_size_seconds = 1  # Desired chunk size in seconds
nperseg = 8192  # 512, 1024, 2048, 4096, 8192
angles = [-70, -60, -50, -40, -30, -20, -10, 0, 10, 20, 30, 40, 50, 60, 70]
pca_components = 5
threshold_multiplier = 15
grid_scale = 0.05
anom_y_lim = 50
baseline_calculations = 5 # first x seconds of audio use as pca threshold baseline
num_channels = len(angles)

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
                principal_components = process_chunk(chunk, nperseg, pca_components)
                principal_components_list[c].append(principal_components)
                f.create_dataset(f'channel_{c}_chunk_{i}', data=principal_components)
        f.attrs['nperseg'] = nperseg
        f.attrs['pca_components'] = pca_components
        f.attrs['chunk_size_seconds'] = chunk_size_seconds
        f.attrs['num_chunks'] = num_chunks

# Calculate baseline statistics for each channel
baseline_means = []
baseline_stds = []

for c in range(num_channels):
    baseline_data = np.vstack(principal_components_list[c][:baseline_calculations])  # Using first x chunks as baseline
    baseline_means.append(np.mean(baseline_data, axis=0))
    baseline_stds.append(np.std(baseline_data, axis=0))

baseline_means = np.array(baseline_means)
baseline_stds = np.array(baseline_stds)

# Set up the figure and axis for the animation
fig = plt.figure(figsize=(32, 8))
gs = fig.add_gridspec(2, num_channels, height_ratios=[1, 1])
axes_pca = []
axes_anomaly = []
sc_list = []
anomaly_texts = []
circles = []

# Initialize scatter plots for each channel
for i in range(num_channels):
    ax_pca = fig.add_subplot(gs[0, i])
    sc = ax_pca.scatter([], [])
    ax_pca.set_xlim(-grid_scale, grid_scale)
    ax_pca.set_ylim(-grid_scale, grid_scale)
    ax_pca.set_xlabel('PC1')
    ax_pca.set_ylabel('PC2')
    ax_pca.set_title(f'Ch {angles[i]}°')
    anomaly_text = ax_pca.text(0.05, 0.95, '', transform=ax_pca.transAxes, ha='left', va='top', color='red')
    sc_list.append(sc)
    anomaly_texts.append(anomaly_text)
    axes_pca.append(ax_pca)

    # Add circle for threshold
    circle = plt.Circle((0, 0), 1, color='blue', fill=False)
    ax_pca.add_artist(circle)
    circles.append(circle)

    ax_anomaly = fig.add_subplot(gs[1, i])
    ax_anomaly.set_xlim(0, num_chunks)
    ax_anomaly.set_ylim(0, anom_y_lim)
    ax_anomaly.set_xlabel('Time (chunks)')
    ax_anomaly.set_ylabel('Anomalies')
    axes_anomaly.append(ax_anomaly)

# Assign colors based on the index of data points
colors = plt.cm.viridis(np.linspace(0, 1, principal_components_list[0][0].shape[0]))

# List to store anomaly counts for each channel
anomaly_counts = np.zeros((num_channels, num_chunks))

chunk_count_update = 0

# Animation update function with threshold detection
def update(frame):
    for i, (sc, anomaly_text, circle, ax_anomaly) in enumerate(zip(sc_list, anomaly_texts, circles, axes_anomaly)):
        global chunk_count_update
        if chunk_count_update%500 == 0:
            print(f'Updating')
        chunk_count_update += 1
        data = principal_components_list[i][frame][:, :2]
        mean = baseline_means[i][:2]
        std = baseline_stds[i][:2]
        threshold_radius = np.linalg.norm(threshold_multiplier * std)

        # Update circle radius and position
        circle.set_radius(threshold_radius)
        circle.set_center(mean)

        # Detect anomalies
        distances = np.linalg.norm(data - mean, axis=1)
        anomalies = distances > threshold_radius

        # Color the anomalies differently
        current_colors = np.array([colors[j] if not anomaly else (1, 0, 0, 1) for j, anomaly in enumerate(anomalies)])
        sc.set_offsets(data)
        sc.set_color(current_colors)

        # Update anomaly count text
        anomaly_count = np.sum(anomalies)
        anomaly_counts[i, frame] = anomaly_count
        anomaly_text.set_text(f'Anomalies: {anomaly_count}')

        # Update the anomaly count plot
        ax_anomaly.plot(np.arange(frame+1), anomaly_counts[i, :frame+1], color='blue')

        # Debugging statement
        if frame < baseline_calculations:
            print(f"Channel {i}, Frame {frame}, Anomalies: {anomaly_count}")

    return sc_list + anomaly_texts + circles + [line for ax in axes_anomaly for line in ax.lines]

# Create the animation
fps = 1 / chunk_size_seconds
ani = animation.FuncAnimation(fig, update, frames=num_chunks, interval=chunk_size_seconds * 1000, blit=True)

# Save the animation to a video file
writer = FFMpegWriter(fps=fps, metadata=dict(artist='Me'), bitrate=1800)
ani.save(filepath_save, writer=writer)
