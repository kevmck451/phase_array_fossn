
import Mic_Array.array_config as array_config
from Filters.audio import Audio

import matplotlib.pyplot as plt
import numpy as np
import time





if __name__ == '__main__':
    start_time = time.time()
    base_path = '/Users/KevMcK/Dropbox/2 Work/1 Optics Lab/2 FOSSN/Data'
    filepath = f'{base_path}/Tests/13_beamformed/diesel_sweep_BF_(-90, 90)-(0, 30).wav'

    field_of_view = (6, 19)
    num_channels = field_of_view[0] * field_of_view[1]
    thetas = [-90, -80, -70, -60, -50, -40, -30, -20, -10, 0, 10, 20, 30, 40, 50, 60, 70, 80, 90]
    phis = [0, 5, 10, 15, 20, 25]

    audio = Audio(filepath=filepath, num_channels=num_channels)
    audio_load_time = time.time() - start_time
    print(f'Audio Load Time: {np.round((audio_load_time / 60), 2)} mins')

    # ----------------------------------------------------------------------------------------------------------------
    pop_time = 0.1 # in seconds
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

    # Initialize matplotlib figure and axis
    fig, ax = plt.subplots(1, 1, figsize=(20, 10))
    cax = ax.imshow(np.flipud(array_rms_pop), cmap='viridis', vmin=0, vmax=0.1)
    fig.colorbar(cax)

    # Set axis labels to represent the intended positions
    ax.set_xticks(np.arange(field_of_view[1]))
    ax.set_yticks(np.arange(field_of_view[0]))
    ax.set_xticklabels(np.linspace(-90, 90, field_of_view[1], dtype=int))
    ax.set_yticklabels(np.flip(np.arange(0, field_of_view[0] * 5, 5, dtype=int)))

    # Counters to keep track of short term and long term indices
    short_term_counter = 0
    long_term_counter = 0

    # Calculate total chunks for short term and long term
    total_short_term_chunks = array_rms_short_term.shape[2]
    total_long_term_chunks = array_rms_long_term.shape[2]

    start_time = time.time()

    while sample_pointer + chunk_size <= audio.num_samples:
        chunk_start_time = time.time()

        chunk_array = audio.data[:, sample_pointer:sample_pointer + chunk_size]
        mean_values = np.mean(np.square(chunk_array), axis=1)
        mean_values[mean_values == 0] = epsilon
        rms_values = np.sqrt(mean_values)

        # Update the RMS pop values based on the channel mapping
        for i in range(field_of_view[0]):
            start_idx = i * field_of_view[1]
            end_idx = start_idx + field_of_view[1]
            array_rms_pop[i, :] = rms_values[start_idx:end_idx]

        # Update short term array
        if short_term_counter < total_short_term_chunks:
            for i in range(field_of_view[0]):
                start_idx = i * field_of_view[1]
                end_idx = start_idx + field_of_view[1]
                array_rms_short_term[i, :, short_term_counter] = rms_values[start_idx:end_idx]
            short_term_counter += 1

        # Update long term array
        if long_term_counter < total_long_term_chunks:
            for i in range(field_of_view[0]):
                start_idx = i * field_of_view[1]
                end_idx = start_idx + field_of_view[1]
                array_rms_long_term[i, :, long_term_counter] = rms_values[start_idx:end_idx]
            long_term_counter += 1

        sample_pointer += chunk_size

        # Reset short term counter if it reaches the max
        if short_term_counter >= total_short_term_chunks:
            short_term_counter = 0

        # Reset long term counter if it reaches the max
        if long_term_counter >= total_long_term_chunks:
            long_term_counter = 0

        # Update the plot with new RMS values
        cax.set_data(np.flipud(array_rms_pop))
        plt.draw()
        plt.pause(0.001)  # Small pause to allow the plot to update

        # Ensure the loop runs at the desired rate
        elapsed_time = time.time() - chunk_start_time
        sleep_time = pop_time - elapsed_time
        if sleep_time > 0:
            time.sleep(sleep_time)

    plt.show()







    end_time = time.time()
    total_time = end_time - start_time


    print(f'Total Time: {np.round((total_time / 60), 2)} mins')


























