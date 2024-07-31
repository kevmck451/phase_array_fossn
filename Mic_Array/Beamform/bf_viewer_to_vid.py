import Mic_Array.array_config as array_config
from Filters.audio import Audio

import matplotlib.pyplot as plt
import numpy as np
import time
from matplotlib.animation import FuncAnimation, FFMpegWriter

if __name__ == '__main__':
    start_time = time.time()
    base_path = '/Users/KevMcK/Dropbox/2 Work/1 Optics Lab/2 FOSSN/Data'
    # filename = 'angel_sweep_BF_(-90, 90)-(0)'
    filename = 'angel_sweep_BF_(-90, 90)-(0)_Pro'
    filepath = f'{base_path}/Tests/16_beamformed/{filename}.wav'
    filepath_save = f'{base_path}/Tests/16_beamformed/{filename}_3.mp4'

    thetas = [-90, -80, -70, -60, -50, -40, -30, -20, -10, 0, 10, 20, 30, 40, 50, 60, 70, 80, 90]
    phis = [0]
    field_of_view = (len(phis), len(thetas))
    num_channels = field_of_view[0] * field_of_view[1]
    rms_max = 0.08

    audio = Audio(filepath=filepath, num_channels=num_channels)
    audio_load_time = time.time() - start_time
    print(f'Audio Load Time: {np.round((audio_load_time / 60), 2)} mins')

    pop_time = 0.5 # in seconds
    short_term_time = 5 # in seconds
    long_term_time = 120 # in seconds

    array_rms_pop = np.zeros((field_of_view[0], field_of_view[1]))
    array_rms_short_term = np.zeros((field_of_view[0], field_of_view[1], int(np.round((short_term_time/pop_time), 0))))
    array_rms_long_term = np.zeros((field_of_view[0], field_of_view[1], int(np.round((long_term_time/pop_time), 0))))

    print(f'RMS_Pop Shape: {array_rms_pop.shape}')
    print(f'RMS_Pop Shape: {array_rms_short_term.shape}')
    print(f'RMS_Pop Shape: {array_rms_long_term.shape}')

    sample_pointer = 0
    chunk_size = int(array_config.sample_rate * pop_time)
    epsilon = 1e-10
    print(f'Chunk Size: {chunk_size}')

    fig, ax = plt.subplots(1, 1, figsize=(20, 10))
    cax = ax.imshow(np.flipud(array_rms_pop), cmap='viridis', vmin=0, vmax=rms_max)
    fig.colorbar(cax)

    ax.set_xticks(np.arange(field_of_view[1]))
    ax.set_yticks(np.arange(field_of_view[0]))
    ax.set_xticklabels(np.linspace(thetas[0], thetas[-1], field_of_view[1], dtype=int))
    if len(phis) > 1:
        ax.set_yticklabels(np.flip(np.arange(0, phis[-1]+1, phis[1]-phis[0], dtype=int)))

    short_term_counter = 0
    long_term_counter = 0

    total_short_term_chunks = array_rms_short_term.shape[2]
    total_long_term_chunks = array_rms_long_term.shape[2]

    def update(frame):
        global sample_pointer, short_term_counter, long_term_counter
        if sample_pointer + chunk_size > audio.num_samples:
            return

        chunk_array = audio.data[:, sample_pointer:sample_pointer + chunk_size]
        mean_values = np.mean(np.square(chunk_array), axis=1)
        mean_values[mean_values == 0] = epsilon
        rms_values = np.sqrt(mean_values)

        for i in range(field_of_view[0]):
            start_idx = i * field_of_view[1]
            end_idx = start_idx + field_of_view[1]
            array_rms_pop[i, :] = rms_values[start_idx:end_idx]

        if short_term_counter < total_short_term_chunks:
            for i in range(field_of_view[0]):
                start_idx = i * field_of_view[1]
                end_idx = start_idx + field_of_view[1]
                array_rms_short_term[i, :, short_term_counter] = rms_values[start_idx:end_idx]
            short_term_counter += 1

        if long_term_counter < total_long_term_chunks:
            for i in range(field_of_view[0]):
                start_idx = i * field_of_view[1]
                end_idx = start_idx + field_of_view[1]
                array_rms_long_term[i, :, long_term_counter] = rms_values[start_idx:end_idx]
            long_term_counter += 1

        sample_pointer += chunk_size

        if short_term_counter >= total_short_term_chunks:
            short_term_counter = 0

        if long_term_counter >= total_long_term_chunks:
            long_term_counter = 0

        cax.set_data(np.flipud(array_rms_pop))

    ani = FuncAnimation(fig, update, frames=range(0, audio.num_samples // chunk_size), repeat=False)
    writer = FFMpegWriter(fps=10, metadata=dict(artist='Me'), bitrate=1800)

    ani.save(filepath_save, writer=writer)

