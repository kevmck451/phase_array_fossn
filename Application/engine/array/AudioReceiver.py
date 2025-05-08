import numpy as np
import threading
import socket
import queue
import time



# ssh -L 7654:192.168.1.201:2048 admin@192.168.1.1

# For collecting RAW data from FPGA server
class AudioReceiver_MicArray:
    def __init__(self, chan_count):
        self.host = "localhost"
        self.port = 7654
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
                self.start_receiving()
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
                try:
                    more = self.sock.recv(min(4096, receive_total - received_len))
                except OSError as e:
                    print(f"Socket error: {e}")
                    self.running = False
                    self.connected = False
                    return
                if not more:
                    print("Socket connection broken")
                    self.running = False
                    self.connected = False
                    return
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