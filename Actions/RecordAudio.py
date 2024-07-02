import numpy as np
import wave
import time
import sys
import select

from Controller.AudioReceiver import AudioReceiver  # Ensure to replace with the actual filename

def save_to_wav(data, sample_rate, chan_count, filename):
    if '.wav' not in filename:
        filename = f'{filename}.wav'

    with wave.open(filename, 'wb') as wf:
        wf.setnchannels(chan_count)
        wf.setsampwidth(2)  # 2 bytes for int16
        wf.setframerate(sample_rate)
        wf.writeframes(data.tobytes())


def main():
    filename = 'test_file_1'
    chan_count = 8
    audio_receiver = AudioReceiver(chan_count)
    audio_receiver.start_receiving()

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
        print("Audio data saved to 'recorded_audio.wav'.")


if __name__ == "__main__":
    main()
