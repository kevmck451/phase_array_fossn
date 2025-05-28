
from Application.controller.event_states import Event
from Application.controller.event_states import State

from dataclasses import dataclass
import threading
import socket
import time


class Server:
    def __init__(self, host='0.0.0.0', port=12345):
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind((self.host, self.port))
        self.socket.listen()
        self.running = False
        self.client_list = []
        self.controller = None
        self.hardware = None
        self.shared_data = {}  # Key: 'audio_raw', 'temp', etc. → Value: string
        self.shared_data_lock = threading.Lock()
        self.request_flags = set()

        print(f"Server listening on {self.host}:{self.port}")

    def start(self):
        threading.Thread(target=self.run, daemon=True).start()

    def handle_client(self, client_socket):
        with client_socket:
            while True:
                data = client_socket.recv(1024)
                if not data:
                    break

                message = data.decode()

                if 'disconnecting' in message:
                    print('client disconnecting')

                if self.controller.app_state != State.RUNNING:
                    client_socket.sendall(b'error\nApp is not running')
                    return

                if 'audio_raw' in message:
                    print(f'Server: Raw Audio Requested')
                    with self.shared_data_lock:
                        self.request_flags.add('audio_raw')
                    print("Server: Waiting for audio...")
                    while True:
                        with self.shared_data_lock:
                            if 'audio_raw' in self.shared_data:
                                requested_data = self.shared_data.pop('audio_raw')
                                self.request_flags.discard('audio_raw')
                                break
                        time.sleep(0.05)
                    header, payload = requested_data
                    client_socket.sendall(b'audio_raw\n' + header.encode() + payload)
                    client_socket.shutdown(socket.SHUT_WR)
                    print(f"Server: Raw Audio Sent")


                elif 'temp' in message:
                    print(f'Server: Temperature Requested')
                    with self.shared_data_lock:
                        self.request_flags.add('temp')
                    print("Server: Waiting for temperature...")
                    while True:
                        with self.shared_data_lock:
                            if 'temp' in self.shared_data:
                                requested_data = self.shared_data.pop('temp')
                                self.request_flags.discard('temp')
                                break
                        time.sleep(0.05)
                    print(f"Sending temperature: {requested_data!r}")
                    client_socket.sendall(b'temp\n' + requested_data.encode())
                    client_socket.shutdown(socket.SHUT_WR)
                    print(f"Server: Temperature Sent")

                elif 'anomaly' in message:
                    print(f'Server: Anomaly Data Requested')
                    with self.shared_data_lock:
                        self.request_flags.add('anomaly')
                    print("Server: Waiting for anomaly...")
                    while True:
                        with self.shared_data_lock:
                            if 'anomaly' in self.shared_data:
                                requested_data = self.shared_data.pop('anomaly')
                                self.request_flags.discard('anomaly')
                                break
                        time.sleep(0.05)
                    client_socket.sendall(b'anomaly\n' + requested_data.encode())
                    client_socket.shutdown(socket.SHUT_WR)
                    print(f"Server: Anomaly Data Sent")

                else:
                    print('data not recognized')
                    client_socket.sendall(b'error\nUnknown request')


    def run(self):
        self.running = True
        while self.running:
            try:
                client_socket, addr = self.socket.accept()
                print('client accepted')
                time.sleep(0.1)
                name = client_socket.recv(1024).decode()

                # check if client name already exists and remove them
                for client_x in self.client_list:
                    if client_x.name == name:
                        self.client_list.remove(client_x)

                client = Client(name=name, socket=client_socket, ip_addr=addr[0], port=addr[1])
                self.client_list.append(client)
                print(f"Connection from {client.name} with address: {addr}")
                client_socket.sendall('ack'.encode())
                threading.Thread(target=self.handle_client, args=(client_socket,), daemon=True).start()
            except Exception as e:
                print(f"Server error: {e}")

    def send_all(self, message: bytes):
        for client in self.client_list:
            try:
                client.socket.sendall(message)
            except Exception as e:
                print(f"Error sending message to {client.name}: {e}")

    def stop(self):
        self.send_all(b'server_disconnecting')
        print('Server Disconnected')
        self.running = False
        self.controller.server_running = False
        self.socket.close()
        self.client_list.clear()




@dataclass
class Client:
    name: str
    socket: object
    ip_addr: str
    port: int

