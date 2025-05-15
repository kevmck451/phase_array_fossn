



import sounddevice as sd
import threading
import queue



class External_Player:
    def __init__(self, mic_streamer, array_config):
        self.mic_streamer = mic_streamer
        self.sample_rate = array_config.sample_rate
        self.channels = 2
        self.running = False
        self.thread = None
        self.stream = None

    def start(self):
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._audio_loop, daemon=True)
            self.thread.start()

    def stop(self):
        self.running = False
        if self.thread and self.thread.is_alive():
            self.thread.join()
        if self.stream:
            self.stream.stop()
            self.stream.close()

    def _audio_loop(self):
        self.stream = sd.OutputStream(samplerate=self.sample_rate, channels=self.channels, dtype='float32')
        self.stream.start()

        while self.running:
            try:
                chunk = self.mic_streamer.external_audio_queue.get(timeout=0.1)
                self.stream.write(chunk)
            except queue.Empty:
                continue
