

from Filters.audio import Audio




from threading import Thread
from queue import Queue
import time





class AudioStreamSimulator:
    def __init__(self, audio_object, chunk_size_sec):

        self.audio_object = audio_object
        self.chunk_size_sec = chunk_size_sec

        self.queue = Queue()
        self.chunk_size = int(self.chunk_size_sec * audio_object.sample_rate)
        self.num_chunks = audio_object.data.shape[1] // self.chunk_size

        self.running = False

    def start_stream(self):
        self.stream_thread = Thread(target=self.stream, daemon=True).start()
        self.running = True

    def stream(self):
        for i in range(self.num_chunks):
            chunk = self.audio_object.data[:, int(i * self.chunk_size):int((i + 1) * self.chunk_size)]
            self.queue.put(chunk)
            time.sleep(self.chunk_size_sec)

        self.running = False





if __name__ == '__main__':
    base_path = '/Users/KevMcK/Dropbox/2 Work/1 Optics Lab/2 FOSSN/Data'
    filename = 'cars_drive_by_150m'
    filepath = f'{base_path}/Tests/17_outdoor_testing/{filename}.wav'
    audio = Audio(filepath=filepath, num_channels=48)
    chunk_size_seconds = 1

    stream = AudioStreamSimulator(audio, chunk_size_seconds)
    stream.start_stream()
    while stream.running:
        if not stream.queue.empty():
            print('PROCESSING----------')
            print(f'Audio Stream Queue Size: {stream.queue.qsize()}')
            current_audio_data = stream.queue.get()
            print(f'Current Data Size: {current_audio_data.shape}')
            print()
            print('='*40)
            print()
        time.sleep(0.5)
