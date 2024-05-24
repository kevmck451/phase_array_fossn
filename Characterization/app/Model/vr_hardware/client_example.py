import socket
from threading import Thread



class Client_Class:
    def __init__(self, server_ip, port):
        self.server_ip = server_ip
        self.port = port
        self.sock = None
        self.connected = False

    def connect(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.sock.connect((self.server_ip, self.port))
            print("Connected to the server successfully.")
            self.connected = True
        except Exception as e:
            print(f"Failed to connect to the server: {e}")
            self.connected = False

    def send_messages(self):
        while self.connected:
            message = input("Enter Data: ")
            if message == 'exit':
                self.disconnect()
                break
            self.sock.sendall(message.encode('utf-8'))

    def receive_messages(self):
        while self.connected:
            try:
                response = self.sock.recv(1024).decode()
                if not response:
                    print("Server has disconnected.")
                    self.disconnect()
                else:
                    print("Received from server:", response)
            except Exception as e:
                print("Error receiving message:", e)
                self.disconnect()

    def disconnect(self):
        self.connected = False
        self.sock.close()
        print("Disconnected from server.")

    def start(self):
        if not self.connected:
            self.connect()
        if self.connected:
            input_thread = Thread(target=self.send_messages)
            # receive_thread = Thread(target=self.receive_messages)

            input_thread.start()
            # receive_thread.start()

            input_thread.join()
            # receive_thread.join()

if __name__ == "__main__":
    print('IP Options: 127.0.0.1 or 192.168.1.253 or 141.225.179.76 or 10.101.124.126')
    ip_input = input('IP Address: ')

    if ip_input == '1':
        ip_address = '127.0.0.1'
    elif ip_input == '2':
        ip_address = '192.168.1.253'
    elif ip_input == '3':
        ip_address = '141.225.179.76'
    elif ip_input == '4':
        ip_address = '10.101.124.126'
    else: ip_address = ip_input

    # client = Client_Class('127.0.0.1', 12345)
    client = Client_Class(ip_address, 12345)

    client.start()










