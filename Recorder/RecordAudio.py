from Controller.AudioReceiver import AudioReceiver
from Recorder.save_to_wav import save_to_wav
from Filters.high_pass import high_pass_filter
from Filters.low_pass import low_pass_filter
from Filters.normalize import normalize
from Filters.audio import Audio

from datetime import datetime
import numpy as np
import time
import sys
import select


def Record_Audio():
    chan_count = 48  # make sure to include -c 8 or -c 16 depending on #
    audio_receiver = AudioReceiver(chan_count)

    collected_data = []
    chunk_duration = 15 * 60  # 10 minutes in seconds
    chunk_samples = chunk_duration * audio_receiver.sample_rate

    chunk_index = 1
    chunk_start_time = datetime.now().strftime("%m-%d-%Y_%I-%M-%S")

    file_path = '/Users/KevMcK/Dropbox/2 Work/1 Optics Lab/2 FOSSN/Data/_Recordings'

    print("Press 's' to stop recording and save to a WAV file.")

    while True:
        if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
            line = input()
            if line.strip().lower() == 's':
                break

        data = audio_receiver.get_audio_data()
        if data is not None:
            collected_data.append(data)
            # print(collected_data)

            # Check if the chunk samples limit is exceeded
            total_samples = sum(len(d) for d in collected_data)
            if total_samples >= chunk_samples:
                all_data = np.vstack(collected_data)

                # # process audio
                # audio_object = Audio(data=all_data, sample_rate=audio_receiver.sample_rate, num_channels=audio_receiver.chan_count)
                # all_data = high_pass_filter(audio_object, cutoff_freq=100)
                # all_data = low_pass_filter(audio_object, cutoff_freq=10000)
                # all_data = normalize(audio_object, 100)

                filename = f"{chunk_start_time}_chunk_{chunk_index}"
                save_to_wav(all_data, audio_receiver.sample_rate, audio_receiver.chan_count, filename)

                # Reset collected data and chunk start time
                collected_data = []
                chunk_index += 1

        time.sleep(0.1)

    # Save any remaining data
    if collected_data:
        all_data = np.vstack(collected_data)

        # # process audio
        # audio_object = Audio(data=all_data, sample_rate=audio_receiver.sample_rate, num_channels=audio_receiver.chan_count)
        # all_data = high_pass_filter(audio_object, cutoff_freq=100)
        # all_data = low_pass_filter(audio_object, cutoff_freq=10000)
        # all_data = normalize(audio_object, 100)

        filename = f"{file_path}/{chunk_start_time}_chunk_{chunk_index}"
        save_to_wav(all_data, audio_receiver.sample_rate, audio_receiver.chan_count, filename)


if __name__ == "__main__":
    Record_Audio()
