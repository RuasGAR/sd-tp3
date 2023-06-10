import socket
import os
from time import sleep
from datetime import datetime
from utils import fill_length

REQUEST_MESSAGE_ID = 1
GRANT_MESSAGE_ID = 2
RELEASE_MESSAGE_ID = 3
COORDINATOR_HOST = "127.0.0.1"
COORDINATOR_PORT = 8088
COORDINATOR_ADDR = (COORDINATOR_HOST,COORDINATOR_PORT)

def connect_to_coordinator(r_times,k_seconds):

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        pid = os.getpid() 
        s.bind((COORDINATOR_HOST, pid))

        initial_message = fill_length(f"{REQUEST_MESSAGE_ID}|{pid}|").encode()
        release_message = fill_length(f"{RELEASE_MESSAGE_ID}|{pid}|").encode()
        
        for r in range(r_times):

            s.sendto(initial_message,COORDINATOR_ADDR)
            # só pode ser mensagem concedendo acesso (GRANT_MESSAGE_ID)
            _data,_addr = s.recvfrom(10) # é bloqueante por natureza
            
            with open('resultado.txt', 'a') as f:
                t_sys = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f") # with milisseconds
                f.write(f"{t_sys} - {pid}\n")
                f.close()

            sleep(k_seconds)
        
            s.sendto(release_message, COORDINATOR_ADDR)

        s.close()

        exit()

if __name__ == "__main__":
    connect_to_coordinator(2,5)