import numpy as np
import socket
import time

def request_data_constantly(port, request_type):
    host = '127.0.0.1'
    BUFFER_SIZE = 8192
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((host, port))
        sock.sendall(b'Client')
        sock.recv(BUFFER_SIZE)  # wait for ack

        sock.sendall(request_type.encode())

        data = b''
        try:
            while True:
                part = sock.recv(BUFFER_SIZE)
                if not part:
                    break
                data += part
        except socket.timeout:
            print("Timeout reached while receiving")

        if request_type == "audio_raw":
            try:
                header, raw = data.split(b'|', 1)
                tag, shape_str = header.decode().split('\n', 1)  # ensure only splits at first newline
                shape = eval(shape_str.strip())  # safely evaluate the shape
                print("Audio shape:", shape)
                raw = raw[:np.prod(shape) * 2]  # trim to exact size in bytes
                audio_array = np.frombuffer(raw, dtype=np.int16).reshape(shape)
                print("Audio snippet:\n", audio_array[:2, :20].astype(np.float32))
            except:
                print("ERROR:", data.decode(errors='replace'))

        else:
            print("Received:", data.decode(errors='replace'))


if __name__ == '__main__':

    LINE_ARRAY_PORT = 32492
    RECT_ARRAY_PORT = 21197

    ports = [LINE_ARRAY_PORT, RECT_ARRAY_PORT]
    request_type = ['audio_raw', 'temp', 'anomaly']

    while True:
        for port in ports:
            for request in request_type:
                request_data_constantly(port, request)
                time.sleep(.25)