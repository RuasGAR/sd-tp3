import logging
import socket
from time import sleep
from utils import fill_length

COORDINATOR_HOST = "127.0.0.1"
COORDINATOR_PORT = 8088

def connect_to_coordinator():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((COORDINATOR_HOST, COORDINATOR_PORT))
        pid = s.getsockname()[1]
        message = fill_length(f"3|{pid}|").encode()
        s.send(message)
        data = s.recv(10).decode("ascii")
        print(data)
        
if __name__ == "__main__":
    connect_to_coordinator()