
import socket


def server_example():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # host = '0.0.0.0'
    host = '192.168.1.253'
    port = 12345
    server_socket.bind((host, port))

    server_socket.listen()
    print('Waiting for Connection...')

    while True:
        client_socket, addr = server_socket.accept()
        print(f"Connection from {addr} has been established.")

        # You can now interact with the client_socket for sending/receiving data
        # For instance, to receive data:
        # data = client_socket.recv(1024)
        # if data:
        #     print("Received:", data.decode('utf-8'))

        # Don't forget to close each client socket when you're done with it
        client_socket.close()

def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('0.0.0.0', 12345))
    server_socket.listen()
    print('Waiting for a connection...')

    client_socket, addr = server_socket.accept()
    print(f"Connection from {addr} established.")

    # Send confirmation to client
    client_socket.sendall("Connection established".encode('utf-8'))

    # Handle client communication
    try:
        while True:
            data = client_socket.recv(1024)
            if not data:
                break  # Client disconnected
            print("Received:", data.decode('utf-8'))
            # Process data here

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        client_socket.close()
        print("Connection closed.")
        server_socket.close()

if __name__ == "__main__":
    start_server()




