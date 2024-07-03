
from Controller.AudioReceiver import AudioReceiver

from datetime import datetime
import numpy as np
import wave
import time
import sys
import select

# For recording RAW data from FPGA
def save_to_wav(data, sample_rate, chan_count, filename):

    if '.wav' not in filename:
        filename = f'{filename}.wav'

    file_path = '/Users/KevMcK/Dropbox/2 Work/1 Optics Lab/2 FOSSN/Data/_Recordings'
    file = f'{file_path}/{filename}'

    with wave.open(file, 'wb') as wf:
        wf.setnchannels(chan_count)
        wf.setsampwidth(2)  # 2 bytes for int16
        wf.setframerate(sample_rate)
        wf.writeframes(data.tobytes())

    print(f'Recording Saved: {file}')

def main():
    chan_count = 8 # 16
    filename = datetime.now().strftime("%m-%d-%Y %I-%M-%S")
    audio_receiver = AudioReceiver(chan_count)

    collected_data = []

    print("Press 's' to stop recording and save to a WAV file.")

    while True:
        if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
            line = input()
            if line.strip().lower() == 's':
                break

        data = audio_receiver.get_audio_data()
        if data is not None:
            collected_data.append(data)
        time.sleep(0.1)

    if collected_data:
        all_data = np.vstack(collected_data)
        save_to_wav(all_data, audio_receiver.sample_rate, audio_receiver.chan_count, filename)


if __name__ == "__main__":
    main()
