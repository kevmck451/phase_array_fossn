


from scipy.signal import resample
import sounddevice as sd
import numpy as np
import threading
import queue



class External_Player:
    def __init__(self, mic_streamer, beamformer, processor, array_config):
        self.mic_streamer = mic_streamer
        self.beamformer = beamformer
        self.processor = processor
        self.array_config = array_config
        self.sample_rate = self.array_config.sample_rate
        self.channels = 2
        self.running = False
        self.thread = None
        self.stream = None
        self.stream_location = None
        self.selected_channels = [0]

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

                chunk = self.select_stream_location()
                chunk = self.select_stereo(chunk)
                chunk = self.prep_for_stream(chunk)

                self.stream.write(chunk)

            except queue.Empty:
                continue

    def select_stream_location(self):
        if self.stream_location == 'Beam':
            chunk = self.beamformer.external_audio_queue.get(timeout=0.1).T.astype(np.float32)
            # print(f'Beam Chunk: {chunk.shape}')

            # Drain others
            try:
                self.processor.external_audio_queue.get_nowait()
            except queue.Empty:
                pass
            try:
                self.mic_streamer.external_audio_queue.get_nowait()
            except queue.Empty:
                pass

        elif self.stream_location == 'Pro':
            raw_chunk = self.processor.external_audio_queue.get(timeout=0.1).T.astype(np.float32)
            chunk = resample(raw_chunk, 48000)  # match expected sample rate
            # print(f'Pro Chunk: {chunk.shape}')

            # Drain others
            try:
                self.beamformer.external_audio_queue.get_nowait()
            except queue.Empty:
                pass
            try:
                self.mic_streamer.external_audio_queue.get_nowait()
            except queue.Empty:
                pass

        else:
            chunk = self.mic_streamer.external_audio_queue.get(timeout=0.1).T.astype(np.float32)
            # print(f'Raw Chunk: {chunk.shape}')

            num_samples = chunk.shape[1]
            spatial_mapped = np.zeros((self.array_config.rows, self.array_config.cols, num_samples))

            for ch_index, (mic_x, mic_y) in enumerate(self.array_config.mic_positions):
                spatial_mapped[mic_x, mic_y, :] = chunk[ch_index, :]
                # print(f'MX{mic_x} | MY{mic_y} <- ch{ch_index + 1}')

            # Drain others
            try:
                self.beamformer.external_audio_queue.get_nowait()
            except queue.Empty:
                pass
            try:
                self.processor.external_audio_queue.get_nowait()
            except queue.Empty:
                pass

        return chunk

    def select_stereo(self, chunk):

        ch = self.selected_channels
        n = len(ch)

        if n == 0:
            left = right = chunk[:, 0]
        elif n == 1:
            idx = ch[0]
            left = right = chunk[:, idx]
        else: # Stereo

            mid = n // 2
            if n % 2 == 0:
                left_idx = ch[:mid]
                right_idx = ch[mid:]
            else:
                left_idx = ch[:mid + 1]  # middle shared to left
                right_idx = ch[mid:]  # middle shared to right

            left = np.sum(chunk[:, left_idx], axis=1)
            right = np.sum(chunk[:, right_idx], axis=1)

        chunk = np.stack((left, right), axis=1)

        return chunk

    def prep_for_stream(self, chunk):
        max_val = np.max(np.abs(chunk))
        if max_val > 1.0:
            chunk = chunk / max_val  # Prevent clipping

        return chunk


































