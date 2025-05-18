

from Application.engine.filters.audio import Audio




from threading import Thread
from queue import Queue
import numpy as np
import time





class AudioStreamSimulator:
    def __init__(self, audio_object, chunk_size_sec):

        self.audio_object = audio_object
        self.chunk_size_sec = chunk_size_sec

        self.queue = Queue()
        self.chunk_size = int(self.chunk_size_sec * audio_object.sample_rate)
        self.num_chunks = audio_object.data.shape[1] // self.chunk_size

        self.running = False
        self.stop_flag = False
        self.realtime = True

        self.send_to_external_audio_stream = False
        self.external_audio_queue = Queue()

        self.record_audio = False
        self.recorded_chunks = []

        self.save_path = None

    def start_stream(self):
        if self.running:
            print("Stream already running. Skipping restart.")
            return
        self.stop_flag = False
        print('starting simulated stream')
        self.running = True
        self.stream_thread = Thread(target=self.stream, daemon=True).start()

    def stream(self):
        for i in range(self.num_chunks):
            if self.stop_flag:
                break
            chunk = self.audio_object.data[:, int(i * self.chunk_size):int((i + 1) * self.chunk_size)]
            self.queue.put(chunk)
            if self.send_to_external_audio_stream:
                self.external_audio_queue.put(chunk)
            if self.record_audio:
                self.recorded_chunks.append(chunk)
            if self.realtime:
                time.sleep(self.chunk_size_sec)

        self.running = False
        self.stop_flag = False

    def save_audio(self):
        full_audio = np.hstack(self.recorded_chunks)
        from scipy.io.wavfile import write
        filepath = f"{self.save_path}/{self.audio_object.name}_calibration.wav"
        write(filepath, self.audio_object.sample_rate, full_audio.T.astype(np.float32))
