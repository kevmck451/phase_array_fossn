

from dataclasses import dataclass
import threading
import socket
import time
import bme280
import smbus2



def get_temp():
    port = 3
    address = 0x76
    bus = smbus2.SMBus(port)

    bme280.load_calibration_params(bus, address)

    bme280_data = bme280.sample(bus, address)
    # date = bme280_data.timestamp.split(" ")[0]
    # time = bme280_data.timestamp.split(' ')[0].split('+')[0].split('.')[0] # need to correct time zone
    # humidity = int(bme280_data.humidity)
    ambient_temperature = int((bme280_data.temperature * 9 / 5) + 32)

    return ambient_temperature



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


    def handle_client(self, client_socket):
        with client_socket:
            while True:
                data = client_socket.recv(1024)
                if not data:
                    break

                message = data.decode()
                if 'heartbeat' in message:
                    pass
                elif 'disconnecting' in message:
                    print('client disconnecting')

                elif 'temp_requested' in message:
                    air_temp = str(get_temp())
                    self.send_all(air_temp)

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
                print(f'sending message: {message}')
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