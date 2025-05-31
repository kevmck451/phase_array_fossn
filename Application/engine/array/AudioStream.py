
from Application.engine.array.AudioReceiver import AudioReceiver_MicArray
from Application.engine.filters.save_to_wav import save_to_wav

from datetime import datetime
from threading import Thread
from queue import Queue
import numpy as np
import traceback
import tempfile
import time
import os



class Mic_Array:
    def __init__(self, array_config):
        self.chan_count = array_config.num_mics
        self.audio_receiver = AudioReceiver_MicArray(self.chan_count, array_config)

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
        self.send_to_external_audio_stream = False
        self.external_audio_queue = Queue()
        self.chunk_size = int(self.chunk_size_sec * array_config.sample_rate)

        self.save_successful = False

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

                if self.send_to_external_audio_stream:
                    self.external_audio_queue.put(data.T)
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

                if self.send_to_external_audio_stream:
                    self.external_audio_queue.put(data.T)
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
        # all_data = np.vstack(self.collected_data)
        # filename = f"{filepath}/{self.chunk_start_time}_chunk_{self.chunk_index}"
        # save_to_wav(all_data, self.audio_receiver.sample_rate, self.audio_receiver.chan_count, filename)

        self.save_successful = False  # default to False at the top
        all_data = None

        try:
            # Ensure target directory exists
            os.makedirs(filepath, exist_ok=True)

            # Stack collected data into a 2D array
            all_data = np.vstack(self.collected_data)

            # Build output filename
            filename = f"{filepath}/{self.chunk_start_time}_chunk_{self.chunk_index}"

            # Save to WAV
            save_to_wav(all_data, self.audio_receiver.sample_rate, self.audio_receiver.chan_count, filename)

            # Mark success
            self.save_successful = True

        except Exception as e:
            print(f"[ERROR] Failed to save to {filepath}. Stashing to fallback. Reason: {e}")

            # Fallback to temp location
            fallback_dir = os.path.join(tempfile.gettempdir(), "failsafe_audio_dumps")
            os.makedirs(fallback_dir, exist_ok=True)

            # Create fallback filename with timestamp and chunk index
            fallback_file = f"{fallback_dir}/{self.chunk_start_time}_chunk_{self.chunk_index}.npy"

            # Save raw data for recovery
            try:
                np.save(fallback_file, all_data)
            except Exception as inner_e:
                print(f"[CRITICAL] Could not save fallback file either: {inner_e}")

            # Optionally log traceback to help with debugging (remove if not needed)
            try:
                with open(fallback_file + ".log", "w") as f:
                    f.write(traceback.format_exc())
            except:
                pass  # silently ignore logging failures