#The server file is modified heavily based on the example shown by Rohan during the 112 mini lecture
import socket
from _thread import *
from queue import Queue

HOST = ''
PORT = 50014
BACKLOG = 2

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen(BACKLOG)

clientete = []
serverChannel = Queue(10000)

def handleClient(client,serverChannel):
    while True:
        msg = client.recv(1000).decode("UTF-8")
        if (msg):
            print(msg)
            serverChannel.put(msg)

def serverThread(clientete, serverChannel):
    while True:
        msg = serverChannel.get(True, None)
        for client in clientete:
            client.send(bytes(msg, 'UTF-8'))

start_new_thread(serverThread, (clientete, serverChannel))

while True:
    client, address = server.accept()
    clientete.append(client)
    print('connection received')
    if len(clientete) == 1:
        client.send(bytes("player1", 'UTF-8'))
    elif len(clientete) == 2:
        client.send(bytes("player2", 'UTF-8'))
        for a in clientete:
            a.send(bytes("start", 'UTF-8'))
    start_new_thread(handleClient, (client,serverChannel))

