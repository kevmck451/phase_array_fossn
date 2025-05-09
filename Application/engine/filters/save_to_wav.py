

import wave

# For recording RAW data from FPGA
def save_to_wav(data, sample_rate, chan_count, filepath):

    if '.wav' not in filepath:
        filepath = f'{filepath}.wav'

    with wave.open(filepath, 'wb') as wf:
        wf.setnchannels(chan_count)
        wf.setsampwidth(2)  # 2 bytes for int16
        wf.setframerate(sample_rate)
        wf.writeframes(data.tobytes())

    print(f'Recording Saved: {filepath}')








