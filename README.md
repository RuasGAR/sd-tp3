# 3º Trabalho Prático de Sistemas Distribuídos (COS470 - Eng.Computação e Informação - UFRJ)

A proposta desta avaliação foi a implementação de um algoritmo de exclusão mútua distribuído, constituído por:

* um Coordenador, responsável por gerenciar acesso a um arquivo de texto;
* múltiplos Participantes, que executam um loop intervalado de pedidos para escrita;

O Coordenador é um programa multithreaded, com uma linha de execução para o socket de comunicação, uma thread rodando o algoritmo de gereneciamento, 
e uma outra para atender comandos do terminal - a exemplo de impressão da fila de pedidos ou do número de vezes em que cada processo já teve um pedido concedido. 
Na thread principal, o algoritmo verifica a fila criada pelos pedidos recebidos no socket e envia as mensagens de concessão de acesso de acordo com a disponibilidade.
Os Participantes, por sua vez, enviam pedido, esperam a resposta, e quando positiva, escrevem o seu PID no arquivo texto supracitado.

O protocolo de comunicação para este projeto foi o UDP, numa tentativa de simplificar o gerenciamento de conexões, tendo em vista que não seria necessário manter conexões abertas.

