import socket
import threading
import queue
import numpy as np
import time


# For collecting RAW data from FPGA server
class AudioReceiver:
    def __init__(self, chan_count):
        self.host = "192.168.1.201"
        self.port = 2048
        self.sample_rate = 48000
        self.chunk_secs = 1.0
        self.chan_count = chan_count
        self.recv_q = queue.Queue(maxsize=10)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.start_receiving()

    def connect(self):
        self.sock.connect((self.host, self.port))

    def recv_thread_fn(self):
        while True:
            received_bits = []
            received_len = 0
            receive_total = int(self.sample_rate * self.chunk_secs) * self.chan_count * 2
            while received_len < receive_total:
                more = self.sock.recv(min(4096, receive_total - received_len))
                if not more:
                    raise RuntimeError("Socket connection broken")
                received_bits.append(more)
                received_len += len(more)
            receive_chunk = np.frombuffer(b"".join(received_bits), dtype=np.uint8)
            receive_chunk = receive_chunk.view(np.int16)
            receive_chunk.shape = (int(self.sample_rate * self.chunk_secs), self.chan_count)
            try:
                self.recv_q.put_nowait(receive_chunk)
            except queue.Full:
                pass

    def start_receiving(self):
        self.connect()
        recv_thread = threading.Thread(target=self.recv_thread_fn, daemon=True)
        recv_thread.start()

    def get_audio_data(self):
        if not self.recv_q.empty():
            return self.recv_q.get()
        return None



# For collecting RAW data from FPGA server
class AudioReceiver_MicArray:
    def __init__(self, chan_count):
        self.host = "192.168.1.201"
        self.port = 2048
        self.connected = False
        self.cancel_attempt = False
        self.sock = None
        self.sample_rate = 48000
        self.chunk_secs = 1.0
        self.chan_count = chan_count
        self.running = False
        self.recv_q = queue.Queue(maxsize=10)
        self.connect_thread = threading.Thread(target=self.connect, daemon=True)
        self.connect_thread.start()


    def connect(self):
        print('Attempting to Connect with FPGA Server')
        while not self.connected and not self.cancel_attempt:
            try:
                self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.sock.connect((self.host, self.port))
                print(f"FPGA: connected to {self.host}:{self.port}")
                self.connected = True
            except Exception as e:
                # print(f"Error connecting to the server: {e}")
                time.sleep(1)  # Retry after a delay
        self.cancel_attempt = False


    def start_receiving(self):
        recv_thread = threading.Thread(target=self.recv_thread_fn, daemon=True)
        recv_thread.start()


    def recv_thread_fn(self):
        self.running = True
        while self.connected:
            received_bits = []
            received_len = 0
            receive_total = int(self.sample_rate * self.chunk_secs) * self.chan_count * 2
            while received_len < receive_total:
                more = self.sock.recv(min(4096, receive_total - received_len))
                if not more:
                    self.running = False
                    raise RuntimeError("Socket connection broken")
                received_bits.append(more)
                received_len += len(more)
            receive_chunk = np.frombuffer(b"".join(received_bits), dtype=np.uint8)
            receive_chunk = receive_chunk.view(np.int16)
            receive_chunk.shape = (int(self.sample_rate * self.chunk_secs), self.chan_count)
            try:
                self.recv_q.put_nowait(receive_chunk)
            except queue.Full:
                pass


    def get_audio_data(self):
        if not self.recv_q.empty():
            return self.recv_q.get()
        return None


    def close_connection(self):
        self.cancel_attempt = True
        self.connected = False
        if self.sock:
            self.sock.close()
            print("FPGA Connection closed")




if __name__ == "__main__":
    chan_count = 48
    audio_receiver = AudioReceiver(chan_count)

    while True:
        data = audio_receiver.get_audio_data()
        if data is not None:
            print("Received audio data chunk with shape:", data.shape)
        time.sleep(0.1)
