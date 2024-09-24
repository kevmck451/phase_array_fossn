
from Mic_Array.Audio_Stream.AudioReceiver import AudioReceiver_MicArray


import Mic_Array.array_config as array_config
from Recorder.save_to_wav import save_to_wav


from datetime import datetime
from threading import Thread
from queue import Queue
import numpy as np
import time



class Mic_Array:
    def __init__(self):
        self.chan_count = 48  # make sure to include -c 8 or -c 16 depending on #
        self.audio_receiver = AudioReceiver_MicArray(self.chan_count)

        self.collected_data = []
        self.chunk_duration = 15 * 60  # 10 minutes in seconds
        self.chunk_samples = self.chunk_duration * self.audio_receiver.sample_rate

        self.chunk_index = 1
        self.chunk_start_time = datetime.now().strftime("%m-%d-%Y_%I-%M-%S")

        self.recording_thread = None
        self.record_running = False
        self.record_audio = False

        self.chunk_size_sec = 1
        self.queue = Queue()
        self.chunk_size = int(self.chunk_size_sec * array_config.sample_rate)


    def start_recording(self, filepath):
        self.record_running = True
        if self.record_audio:
            self.recording_thread = Thread(target=self.record_save, args=(filepath, ), daemon=True).start()
        else:
            self.recording_thread = Thread(target=self.record, daemon=True).start()

    def record(self):
        while self.record_running:
            data = self.audio_receiver.get_audio_data()
            if data is not None:

                self.queue.put(data.T)
                # print(data.shape)

            time.sleep(0.1)

    def record_save(self, filepath):
        self.chunk_start_time = datetime.now().strftime("%m-%d-%Y_%I-%M-%S")
        while self.record_running:
            data = self.audio_receiver.get_audio_data()
            if data is not None:
                self.collected_data.append(data)
                # print(collected_data)

                self.queue.put(data.T)
                # print(data.shape)

                # Check if the chunk samples limit is exceeded
                total_samples = sum(len(d) for d in self.collected_data)
                if total_samples >= self.chunk_samples:
                    self.save_data(filepath)

                    # Reset collected data and chunk start time
                    self.collected_data = []
                    self.chunk_index += 1

            time.sleep(0.1)

        # Save any remaining data
        if self.collected_data: self.save_data(filepath)


    def save_data(self, filepath):
        all_data = np.vstack(self.collected_data)
        filename = f"{filepath}/{self.chunk_start_time}_chunk_{self.chunk_index}"
        save_to_wav(all_data, self.audio_receiver.sample_rate, self.audio_receiver.chan_count, filename)