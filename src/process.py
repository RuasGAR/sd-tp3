import socket
import os
from time import sleep
from datetime import datetime
from utils import fill_length
from multiprocessing import Process

REQUEST_MESSAGE_ID = 1
GRANT_MESSAGE_ID = 2
RELEASE_MESSAGE_ID = 3
COORDINATOR_HOST = "127.0.0.1"
COORDINATOR_PORT = 8088
COORDINATOR_ADDR = (COORDINATOR_HOST, COORDINATOR_PORT)

def log_message(action, m_type, source, destination):
    t_sys = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f") # with milliseconds
    print(f"{t_sys} - {action} - {m_type} - Source: {source} - Destination: {destination}\n")

def connect_to_coordinator (r_times, k_seconds):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        pid = os.getpid()
        print(f"Oi, meu PID é {pid}\n")

        s.bind((COORDINATOR_HOST, pid)) # Associa a um endereço aleatório para evitar conflitos

        #port = s.getsockname()[1]

        initial_message = fill_length(f"{REQUEST_MESSAGE_ID}|{pid}|").encode()
        release_message = fill_length(f"{RELEASE_MESSAGE_ID}|{pid}|").encode()

        for r in range(r_times):

            s.sendto(initial_message, COORDINATOR_ADDR)
            log_message("Sent", "REQUEST", pid, COORDINATOR_PORT) # Gera um print no terminal

            # Capturar o valor recebido na resposta
            _data, _ = s.recvfrom(10)

            m_type, destination, _ = _data.decode("ascii").split('|')
            destination = int(destination)
            log_message("Received", "GRANT", destination, pid)

            # Região crítica do processo cliente
            print(f"Process {pid} entering critical section...")
            # Abrir o arquivo e escrever o identificador do processo e a hora atual com milissegundos
            with open('src/resultado.txt', 'a') as f:
                t_sys = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")  # with milisseconds
                f.write(f"Process {pid} - {t_sys}\n")
                f.close()

            # Aguardar k segundos
            sleep(k_seconds)

            # Enviar mensagem de liberação ao coordenador
            s.sendto(release_message, COORDINATOR_ADDR)  # Envia mensagem de liberação
            log_message("Sent", "RELEASE", pid, COORDINATOR_PORT)

        s.close()
        exit()

def start_processes(n, rep, k):
    processes = []
    for _ in range(n):
        process = Process(target=connect_to_coordinator, args=(rep, k))
        processes.append(process)
        process.start()
    for process in processes:
        process.join()  # Aguarda o término de todas as threads

if __name__ == "__main__":
    num_threads = 2  # Número de processos
    repetitions = 2  # Número de vezes que cada processo entra na região crítica
    k = 1  # Tempo em segundos que cada processo fica na região crítica

    start_processes(num_threads, repetitions, k)
