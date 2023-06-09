import threading
import logging
import socket
import queue
from utils import fill_length

format = "%(asctime)s - %(levelname)s - %(message)s"
logging.basicConfig(
    filename='coordinator-logs.txt',
    filemode='w',
    format=format, 
    level=logging.DEBUG,
    datefmt='%Y-%m-%d %H:%M:%S'
)

# CONSTANTES
GRANT = 2
HOST = "127.0.0.1"
PORT = 8088
GRANT_MESSAGE = fill_length(f"{GRANT}|{PORT}|").encode()

# [VARIÁVEIS GLOBAIS]
request_queue = queue.Queue()
queue_mutex = threading.Semaphore(1)
# dicionário aninhado a ser preenchido da seguinte forma {client_addr:{socket_conn, counter}}
connections = {} 
connections_mutex = threading.Semaphore(1)
message = ""
message_mutex = threading.Semaphore(1)
message_arrived = threading.Event()
kill_program = False


def server_handler():

    """ 
        Inicia um servidor de conexões TCP, responsável por receber clientes
        e encaminhar seu conteúdo ao algoritmo de exclusão mútua distribuído.
    """
    
    global connections, connections_mutex 
    global request_queue, queue_mutex 
    global message, message_mutex
    global kill_program

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    with server_socket as s:
        s.bind((HOST,PORT))
        s.listen()
        logging.info(f"O servidor foi iniciado no endereço {HOST}:{PORT}.")

        while kill_program == False:
            conn, addr = s.accept()
            # Como a princípio usamos sempre o mesmo IP, vamos usar as portas como único
            # identificador de endereço em serviço
            addr_port = addr[1]
            connections_mutex.acquire()
            if addr_port not in connections.keys():
                connections[addr_port] = {"socket_conn":conn, "counter":0}
            connections_mutex.release()
            
            logging.info(f"O endereço {addr_port} estabeleceu conexão com o servidor.")
            message_mutex.acquire()
            message = conn.recv(10).decode("ascii")
            message_mutex.release()
            logging.info(f"Mensagem recebida: {message}; Origem: {addr_port}")
            message_arrived.set()   
        
        s.close()
    logging.info("Servidor encerrado.")
    exit()

def terminal_handler():
    """ 
        Função de background para interface com usuário.
        O processamento do input segue as recomendações do enunciado do trabalho.
    """

    global queue_mutex,request_queue
    global connections,connections_mutex
    global kill_program

    instructions = [
        "1)Imprimir o estado atual da fila de pedidos",
        "2)Imprimir quantidade de vezes em que cada processo foi atendido",
        "3)Finalizar programa coordenador"
    ]

    while kill_program == False:    

        # Grid de comandos básicos
        print("Digite o número correspondente para acionar alguma das instruções abaixo:")
        for inst in instructions:
            print(inst)

        # Tomando input
        try:
            command = int(input())
        except Exception as e:
            logging.exception("Um erro ocorreu ao fazer a leitura do comando. Veja mais informações abaixo.")
            print(e)
            continue # próxima iteração do while

        # Tratamento de ações
        if (command == 1):
            print("Você selecionou a opção 1!\n")
            queue_mutex.acquire()
            print(f"A fila de pedidos possui {request_queue.qsize()} itens. São eles:")
            for request in request_queue.queue:
                print(request)
            queue_mutex.release()
            print('\n')
            
        elif (command == 2):
            print("Você selecionou a opção 2!\n")
            connections_mutex.acquire()
            for p,info in connections.items():
                print(f"Processo {p}: {info['counter']} pedidos concedidos.")
            connections_mutex.release()
            print('\n')
        
        elif (command == 3):
            print("Você selecionou a opção 3!\n")
            kill_program = True
            


if __name__ == "__main__":

    terminal = threading.Thread(target=terminal_handler, name="terminal", daemon=True)
    server = threading.Thread(target=server_handler, name="server", daemon=True)

    terminal.start()
    server.start()

    # main algorithm
    while kill_program == False:
        
        message_arrived.wait(timeout=10)        

        message_mutex.acquire()
        m_type,pid,_ = message.split('|')
        message_mutex.release()
        pid = int(pid)

        if m_type == 1: # release 
            
            # pega o próximo da fila
            queue_mutex.acquire()
            if not request_queue.empty():
                next_client_id = request_queue.get()
            queue_mutex.release()

            # faz o envio da mensagem de liberação
            connections_mutex.acquire()
            connections[next_client_id]["socket_conn"].send(GRANT_MESSAGE)
            connections_mutex[next_client_id]["counter"] += 1
            connections_mutex.release()
            logging.info(f"Mensagem enviada: {str(GRANT_MESSAGE)}; Destino: {next_client_id}")

        else: # automaticamente, é um pedido
            
            queue_mutex.acquire()

            if request_queue.empty():
                connections_mutex.acquire()
                connections[pid]["socket_conn"].send(GRANT_MESSAGE)
                connections[pid]["counter"] += 1
                connections_mutex.release()
                logging.info(f"Mensagem enviada: {str(GRANT_MESSAGE)}; Destino: {pid}")
            else:
                request_queue.put(pid)
            
            queue_mutex.release()
        
        message_arrived.clear()

    exit()