import threading
import logging
import socket
import queue

format = "%(asctime)s - %(levelname)s - %(message)s"
logging.basicConfig(filename='log.txt',format=format, level=logging.DEBUG,datefmt='%Y-%m-%d %H:%M:%S')

# Variáveis globais
request_queue = queue.Queue()
queue_mutex = threading.Semaphore(1)
# dicionário aninhado a ser preenchido da seguinte forma {client_addr:{socket_conn, counter}}
connections = {} 
connections_mutex = threading.Semaphore(1)
kill_event = threading.Event()


def build_server(host, port):

    """ 
        Dados host e port, inicia um servidor de conexões TCP, responsável por receber clientes
        e encaminhar seu conteúdo ao algoritmo de exclusão mútua distribuído.
    """
    
    global connections, connections_mutex, queue_mutex, request_queue 

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((host,port))
        s.listen()
        logging.info(f"O servidor foi iniciado no endereço {host}:{port}.")

        while True:
            conn, addr = s.accept()
            # Como a princípio usamos sempre o mesmo IP, vamos usar as portas como único
            # identificador de endereço em serviço
            addr_port = addr[1]

            connections_mutex.acquire()
            if addr_port not in connections.keys():
                connections[addr_port] = {"socket_conn":conn}
            connections_mutex.release()
            with conn:
                logging.info(f"O endereço {addr_port} estabeleceu conexão com o servidor.")
                # incluir algum tratamento de erro
                data = conn.recv(1024).decode("ascii")
                #print(f"data {data}")
                

def terminal_watcher():
    """ 
        Recebe um evento (Threading.Event) e uma instrução (int) selecionada via terminal.
        Executa as devidas ações de acordo com o enunciado do trabalho.
    """

    global queue_mutex,request_queue
    global connections,connections_mutex
    global kill_event

    instructions = [
        "1)Print current state of the request queue",
        "2)Print how many times each client process has been answered",
        "3)Terminate coordinator program"
    ]

    while True:    
    
        # Grid de comandos básicos
        print("Digite o número correspondente para acionar alguma das instruções abaixo:")
        for inst in instructions:
            print(inst)
        print('\n')

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
                print(f"Process on address {p}: {info} requests answered.")
            connections_mutex.release()
            print('\n')
        
        elif (command == 3):
            print("Você selecionou a opção 3!\n")
            try:
                check = int(input("Você tem certeza que deseja encerrar o programa? (1 - Sim; 2- Não)"))
            except Exception as e:
                logging.exception("Um erro ocorreu ao fazer a leitura do comando. Veja mais informações abaixo.")
                print(e)
                continue

            if check == 1:
                kill_event.set()
            else:
                continue       
            


if __name__ == "__main__":

    thread_map = {
        "terminal_watcher":terminal_watcher,
        "server":build_server
    }

    terminal_handler = threading.Thread(target=thread_map["terminal_watcher"])
    server = threading.Thread(target=thread_map["server"],args=("127.0.0.1",8088))

    terminal_handler.start()
    server.start()

    server.join()
    terminal_handler.join()

    # main algorithm
    