import threading
import logging
import socket
import queue
from utils import fill_length

format = "%(asctime)s.%(msecs)03d - %(levelname)s - %(message)s"
logging.basicConfig(
    filename='coordinator-logs.txt',
    filemode='w',
    format=format, 
    level=logging.DEBUG,
    datefmt='%Y-%m-%d %H:%M:%S'
)

# CONSTANTES
REQUEST_MESSAGE_ID = 1
GRANT_MESSAGE_ID = 2
RELEASE_MESSAGE_ID = 3
HOST = "127.0.0.1"
PORT = 8088
GRANT_MESSAGE = fill_length(f"{GRANT_MESSAGE_ID}|{PORT}|")

# [VARIÁVEIS GLOBAIS]
request_queue = queue.Queue()
message_queue = queue.Queue()

# dicionário aninhado a ser preenchido da seguinte forma {client_addr:{socket_conn, counter}}
connections = {}
connections_mutex = threading.Semaphore(1)
critical_area_in_use = False
kill_program = False



def server_handler():

    """ 
        Inicia um servidor de conexões UDP, responsável por receber clientes
        e direcionar o conteúdo de suas mensagens ao algoritmo de exclusão mútua distribuído,
        no formato de mailbox (na prática, uma fila).
    """

    global request_queue
    global kill_program

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    with server_socket as s:
        
        s.bind((HOST,PORT))
        logging.info(f"O servidor foi iniciado no endereço {HOST}:{PORT}.")

        while kill_program == False:
            
            data, addr = s.recvfrom(10)
            data = data.decode("ascii")
            m_type, _, _ = data.split('|')

            m_type = int(m_type)
            # Considerando máquinas sempre no mesmo IP, só utilizamos a porta como identificador 
            addr_port = int(addr[1])

            # Adicionando o endereço ao dicionário de gerenciamento
            connections_mutex.acquire()
            if addr not in connections.keys():
                connections[addr_port] = {"counter":0}
            connections_mutex.release()
            
            # Fila de mensagens
            message = (m_type, addr_port)
            message_queue.put(message)

            if m_type == REQUEST_MESSAGE_ID:
                logging.info(f"Mensagem recebida: [R] Request {data}; Origem: {addr_port}")
            elif m_type == RELEASE_MESSAGE_ID:
                logging.info(f"Mensagem recebida: [R] Release {data}; Origem: {addr_port}")                    
                
        s.close()

    logging.info("Servidor encerrado.")
    exit()

def terminal_handler():
    """ 
        Função de background para interface com usuário.
        O processamento do input segue as recomendações do enunciado do trabalho.
    """

    global request_queue
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
            print(f"A fila de pedidos possui {request_queue.qsize()} itens. São eles:")
            for request in request_queue.queue:
                print(request)
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
            print("O processo coordenador será encerrado.\n")
            kill_program = True
            


if __name__ == "__main__":

    terminal = threading.Thread(target=terminal_handler, name="terminal", daemon=True)
    server = threading.Thread(target=server_handler, name="server", daemon=True)

    terminal.start()
    server.start()

    """ 
        Parte 1: Caixa de Mensagens 
            
            - Uma única mensagem é processada por iteração.
                -> Se for do tipo RELEASE, toma-se a imediata ação de comunicar ao próximo processo da fila que a
                  região crítica já pode ser utilizada.
                -> Já se for do tipo REQUEST, o processo é devidamente colocado na fila de pedidos.

            - Se a caixa estiver vazia, pula logo para a segunda parte.
        
        Parte 2: Fila de Pedidos 
            
            - De forma resumida, caso tenha algum processo na fila, ele terá permissão de acesso concedida. Do contrário,
              continua-se a execução (dando início a nova iteração)
       
    """

    # main algorithm

    while kill_program == False:
        
        if not message_queue.empty():

            # Mensagens já serão colocadas como tupla (tipo_de_mensagem, endereço)
            message = message_queue.get()
            m_type,pid = message

            if m_type == RELEASE_MESSAGE_ID: # release 
                
                # pega o próximo da fila
                if not request_queue.empty():
                    
                    next_client_id = request_queue.get()
                    
                    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                        s.sendto(GRANT_MESSAGE.encode(),(HOST,next_client_id))
                    
                    logging.info(f"Mensagem enviada: [S] Grant {GRANT_MESSAGE}; Destino: {next_client_id}")
                    
                    connections_mutex.acquire()
                    connections[next_client_id]["counter"] += 1
                    connections_mutex.release()

                else:
                    critical_area_in_use = False
                    logging.info("Fila de pedidos vazia. Nenhum processo em espera.")

            else: # automaticamente, é um pedido (REQUEST_MESSAGE_ID)

                if request_queue.empty() and not critical_area_in_use: 
                    
                    # Concede acesso imediato
                    critical_area_in_use = True
                    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                        s.sendto(GRANT_MESSAGE.encode(),(HOST,pid))

                    logging.info(f"Mensagem enviada: [S] Grant {GRANT_MESSAGE}; Destino: {pid}")
                    
                    # Contabiliza acessos
                    connections_mutex.acquire()
                    connections[pid]["counter"] += 1
                    connections_mutex.release()

                else: # vai pra fila
                    request_queue.put(pid)
        
        if not critical_area_in_use:

            if not request_queue.empty():
                
                next_client_id = request_queue.get()

                with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                    s.sendto(GRANT_MESSAGE.encode(),(HOST,next_client_id))

                logging.info(f"Mensagem enviada: [S] Grant {GRANT_MESSAGE}; Destino: {next_client_id}")
                    
                # Contabiliza acessos
                connections_mutex.acquire()
                connections[next_client_id]["counter"] += 1
                connections_mutex.release()

    exit()