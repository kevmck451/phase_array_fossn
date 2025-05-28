

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

                elif 'audio_raw' in message:
                    print(f'Sending Raw Audio')
                    requested_data = ''
                    self.send_all(requested_data)

                elif 'temp' in message:
                    print(f'Sending Temperature')
                    requested_data = ''
                    self.send_all(requested_data)

                elif 'anomaly' in message:
                    print(f'Sending Anomaly Data')
                    requested_data = ''
                    self.send_all(requested_data)

                else:
                    print('data not recognized')


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


    def send_all(self, message):
        for client in self.client_list:
            try:
                # print(f'sending message: {message}')
                client.socket.sendall(message.encode())
            except Exception as e:
                print(f"Error sending message to {client.name}: {e}")


    def stop(self):
        self.send_all('server_disconnecting')
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




# To run the server
if __name__ == '__main__':
    server = Server('0.0.0.0')
    server.run()