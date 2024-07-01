

from audio import Audio



import numpy as np


sample_rate = 48000
mic_array_rows = 4
mic_array_cols = 4
number_channels = mic_array_rows * mic_array_cols


basepath = '/Users/KevMcK/Dropbox/2 Work/1 Optics Lab/2 FOSSN/Data'
audio_filepath = f'{basepath}/Convolver/test_file.wav'


audio = Audio(filepath=audio_filepath, num_channels=number_channels)
# print(audio)
# audio.waveform(display=True)

# reconfigure audio.data array to match their positions in space
print(audio.data.shape)

reshaped_array = np.zeros((mic_array_rows, mic_array_cols, audio.data.shape[1]))

# Assign channels from the original array to the new array
reshaped_array[0, 0, :] = audio.data[1, :]
reshaped_array[1, 0, :] = audio.data[0, :]
reshaped_array[0, 1, :] = audio.data[3, :]
reshaped_array[1, 1, :] = audio.data[2, :]
reshaped_array[2, 0, :] = audio.data[5, :]
reshaped_array[3, 0, :] = audio.data[4, :]
reshaped_array[2, 1, :] = audio.data[7, :]
reshaped_array[3, 1, :] = audio.data[6, :]
reshaped_array[0, 2, :] = audio.data[9, :]
reshaped_array[1, 2, :] = audio.data[8, :]
reshaped_array[0, 3, :] = audio.data[11, :]
reshaped_array[1, 3, :] = audio.data[10, :]
reshaped_array[2, 2, :] = audio.data[13, :]
reshaped_array[3, 2, :] = audio.data[12, :]
reshaped_array[2, 3, :] = audio.data[15, :]
reshaped_array[3, 3, :] = audio.data[14, :]


# using 16 mics and beamforming to create a single audio channel of a focused area in space

def report_RMS_threshold_reached(audio_data):

    chunk_size = sample_rate // 10
    chunk_pointer = 0
    while True:
        buffer = audio_data[chunk_pointer : chunk_pointer + chunk_size]

        rms = np.sqrt(np.mean(buffer**2))

        if rms > 0.4:
            time = np.round((chunk_pointer / sample_rate), 2)
            print(time)
            return time

        chunk_pointer = chunk_pointer + chunk_size


for channel in audio.data:
    report_RMS_threshold_reached(channel)



