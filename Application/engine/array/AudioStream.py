
from Application.engine.array.AudioReceiver import AudioReceiver_MicArray
from Application.engine.filters.save_to_wav import save_to_wav

from datetime import datetime
from threading import Thread
from queue import Queue
import numpy as np
import time



class Mic_Array:
    def __init__(self, array_config):
        self.chan_count = array_config.num_mics
        self.audio_receiver = AudioReceiver_MicArray(self.chan_count, array_config.sample_rate)

        self.collected_data = []
        self.chunk_duration = array_config.chunk_duration
        self.chunk_samples = self.chunk_duration * array_config.sample_rate

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
        while self.audio_receiver.get_audio_data() is not None:
            x = self.audio_receiver.get_audio_data()
        while self.record_running:
            data = self.audio_receiver.get_audio_data()
            if data is not None:

                self.queue.put(data.T)
                # print(data.shape)

            time.sleep(0.1)

    def record_save(self, filepath):
        while self.audio_receiver.get_audio_data() is not None:
            print('Emptying Queue')
            x = self.audio_receiver.get_audio_data()
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