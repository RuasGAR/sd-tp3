import threading
import logging
import socket

logging.basicConfig(level=logging.INFO)


def build_server(host, port):

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((host,port))
        s.listen()
        logging.info(f"O servidor foi iniciado no endereço {host}:{port}.")

        conn, addr = s.accept()
        with conn:
            logging.info(f"O endereço {addr} estabeleceu conexão com o servidor.")
            data = conn.recv(1024).decode("ascii")
            print(f"data {data}")
            # especificar o que o servidor vai precisar fazer a cada connexão.



if __name__ == "__main__":
    build_server("127.0.0.1",8088)
