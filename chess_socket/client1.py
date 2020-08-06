import socket
import sys
import time

HEADER = 64
FORMAT = 'utf-8'
PORT = 5050
#For getting machine ip address
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect(("8.8.8.8", 80))
SERVER = s.getsockname()[0]
s.close()
ADDR = (SERVER, PORT)
DISCONNECT_MSG = "!disconnect"



MODE = ''
audiance_mode = 'audiance'

def send(msg, client):
    msg_length = len(msg)
    msg_length = str(msg_length).encode(FORMAT)
    msg_length += b' ' * (HEADER - len(msg_length))
    msg = msg.encode(FORMAT)
    client.send(msg_length)
    client.send(msg)

def recv(client):
    msg_length = client.recv(HEADER).decode(FORMAT)
    if msg_length:
        msg_length = int(msg_length)
        msg = client.recv(msg_length).decode(FORMAT)
    return msg

if __name__ == "__main__":
    
    #connecting to the server
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(ADDR)

    MODE = recv(client)
    print(MODE)
    test = 1
    while True:
        if MODE != audiance_mode:
            turn = recv(client)
            print(turn)
            if turn != 'waiting':
                if (turn == MODE):
                    if test == 1 and MODE == 'white':
                        print("Other connected")
                        test = 2
                    msg = input()
                    send(msg, client)
                message = recv(client)
                print(message)
                # print('dfs')

            else:
                print("Waiting for other")
        
        else:
            turn = recv(client)
            if turn:
                print(turn)
                turn = ''
            msg = recv(client)
            if msg:
                print(msg)
                msg = ''
    