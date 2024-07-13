
import wave
import numpy as np


def save_to_wav(data, sample_rate, chan_count, filepath):
    if '.wav' not in filepath:
        filepath = f'{filepath}.wav'

    # Ensure the data is in the correct format
    if data.dtype != np.int16:
        data = (data * 32767).astype(np.int16)

    # Flatten the data for multi-channel audio
    interleaved = np.zeros((data.shape[1] * chan_count,), dtype=np.int16)
    for i in range(chan_count):
        interleaved[i::chan_count] = data[i]

    with wave.open(filepath, 'wb') as wf:
        wf.setnchannels(chan_count)
        wf.setsampwidth(2)  # 2 bytes for int16
        wf.setframerate(sample_rate)
        wf.writeframes(interleaved.tobytes())

    print(f'Recording Saved: {filepath}')







# from pathlib import Path
# import wave
#
# # For recording RAW data from FPGA
# def save_to_wav(data, sample_rate, chan_count, filepath):
#
#     if '.wav' not in filepath:
#         filepath = f'{filepath}.wav'
#
#     with wave.open(filepath, 'wb') as wf:
#         wf.setnchannels(chan_count)
#         wf.setsampwidth(2)  # 2 bytes for int16
#         wf.setframerate(sample_rate)
#         wf.writeframes(data.tobytes())
#
#     print(f'Recording Saved: {filepath}')

