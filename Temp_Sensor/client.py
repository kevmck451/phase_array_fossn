


import socket
import threading
import time

class Sender_Client:
    def __init__(self, host='192.168.1.1', port=12345, name='unknown'):
        self.host = host #
        self.port = port
        self.name = name
        self.connected = False
        self.socket = None
        self.cancel_attempt = False
        self.connect_thread = threading.Thread(target=self.ensure_connection, daemon=True)
        self.connect_thread.start()
        self.heartbeat_thread = threading.Thread(target=self.heartbeat, daemon=True)
        self.heartbeat_attempt = 0
        self.wait_for_response_thread = threading.Thread(target=self.wait_for_response, daemon=True)
        self.request_temp_thread = threading.Thread(target=self.request_temp, daemon=True)
        self.temp_record = []
        self.current_temp = None
        self.temp_sample_time = 5

    def ensure_connection(self):
        print('Attempting to Connect with Temp Server')
        while not self.connected and not self.cancel_attempt:
            try:
                self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.socket.connect((self.host, self.port))
                handshake_message = f'{self.name}'
                self.socket.sendall(handshake_message.encode())
                response = self.socket.recv(1024)
                if not response.decode('utf-8') == 'ack': continue
                print(f"Temp: Connected to {self.host}:{self.port}")
                self.connected = True

                self.heartbeat_thread.start()
                self.request_temp_thread.start()
                self.wait_for_response_thread.start()

            except Exception as e:
                # print(f"Error connecting to the server: {e}")
                time.sleep(1)  # Retry after a delay
        self.cancel_attempt = False

    def heartbeat(self):
        print('heartbeat')
        wait_time = 1
        burst_time = 0.1

        while self.connected:
            # print('beating')
            try:
                self.socket.sendall('heartbeat'.encode())
                time.sleep(burst_time)
                self.socket.sendall('heartbeat'.encode())
                time.sleep(burst_time)
                self.socket.sendall('heartbeat'.encode())
                self.heartbeat_attempt = 0
            except socket.error as e:
                print(f'heartbeat failed attempt: {self.heartbeat_attempt}')
                self.heartbeat_attempt += 1

            if self.heartbeat_attempt == 4:
                print('HARDWARE DISCONNECTED')
                self.connected = False

            time.sleep(wait_time)

    def send_data(self, message):
        if self.connected:
            try:
                self.socket.sendall(message.encode('utf-8'))
                # print("message sent")
            except socket.error as e:
                print(f"Error sending data: {e}")
                self.connected = False
                self.socket.close()
        else:
            print("Not connected. Unable to send data.")

    def wait_for_response(self):
        while self.connected:
            try:
                response = self.socket.recv(1024).decode()
                # print(response)
                if 'server_disconnecting' in response:
                    self.connected = False
                elif 'heartbeat' in response:
                    pass
                else:
                    try:
                        self.current_temp = int(response)
                        self.temp_record.append(self.current_temp)
                    except:
                        print(f'Message: {response}')
            except OSError as e:
                if e.errno == 9:  # Bad file descriptor error

                    print("Socket already closed.")
                else:
                    raise  # Re-raise any unexpected errors
                self.connected = False

    def request_temp(self):
        while self.connected:
            self.send_data('temp_requested')
            time.sleep(self.temp_sample_time)

    def close_connection(self):
        try:
            self.socket.sendall('disconnecting'.encode())
            self.cancel_attempt = True
            self.connected = False
            if self.socket:
                self.socket.close()
                print("Temp Sensor Connection closed")
        except:
            self.cancel_attempt = True
            self.connected = False
            if self.socket:
                self.socket.close()
                print("Temp Sensor Connection closed")

# Usage example
if __name__ == '__main__':

    # for running pi to pi
    client = Sender_Client('192.168.1.1', name='Pi-Nix')

    while not client.connected:
        # print("Waiting for connection...")
        time.sleep(1)

    print("Client connected, can send data now.")
    while True:
        command = input('Enter Command: ')
        if command.lower() == 'exit': break
        client.send_data(command)