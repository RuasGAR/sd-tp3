import logging
import socket

COORDINATOR_HOST = "127.0.0.1"
COORDINATOR_PORT = 8088

def connect_to_coordinator():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((COORDINATOR_HOST, COORDINATOR_PORT))
        # faz algo
        #s.send("coe".encode())

if __name__ == "__main__":
    connect_to_coordinator()