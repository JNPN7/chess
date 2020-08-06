import socket
import threading
from time import sleep
import json

HEADER = 64
FORMAT = 'utf-8'
PORT = 5051
#For getting machine ip address
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect(("8.8.8.8", 80))
SERVER = s.getsockname()[0]
s.close()
ADDR = (SERVER, PORT)
DISCONNECT_MSG = "!disconnect"

#building sever at ip SERVER and port PORT
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)

client_list = []
player_client_list = [] #list of dict dict={conn, addr, player_piece}
player_piece = ['white']

global white_turn
white_turn = True

def connect_client():
    while True:
        conn, addr = server.accept()
        client_list.append(conn)
        print(f'[NEW CONNECTION]  {addr}')
        if len(player_client_list) < 2:
            player_dict = {
                'conn': conn,
                'addr': addr,
                'player_piece': player_piece[0]
            }
            player_client_list.append(player_dict)
            send(player_piece[0], conn)
            player_piece[0] = 'black'    
        else:
            send('audiance', conn)

def send(msg, conn):
    msg_length = len(msg)
    msg_length = str(msg_length).encode(FORMAT)
    msg_length += b' ' * (HEADER - len(msg_length))
    msg = msg.encode(FORMAT)
    conn.send(msg_length)
    conn.send(msg)  

def recv(conn):
    msg_length = conn.recv(HEADER).decode(FORMAT)
    if msg_length:
        msg_length = int(msg_length)
        msg = conn.recv(msg_length).decode(FORMAT)
    print('msg')
    return msg

def start():
    print('[STARTING] server is starting...')
    server.listen() 
    print(f'[LISTENING] server is listening at {SERVER}')
    thread_connect_client = threading.Thread(target=connect_client)
    thread_connect_client.start()

def toggle_turn(turn):
    if turn == 'white':
        turn = 'black'
    else:
        turn = 'white'
    return turn

def main():
    send_turn_msg = True
    turn =  'white'
    waiting = True
    while True:
        if len(player_client_list) == 2:
            if send_turn_msg:
                for client in client_list:
                    send(turn, client)
                send_turn_msg = False
            # print(turn)
            if turn == 'white':
                msg = recv(player_client_list[0]['conn'])
            else:
                msg = recv(player_client_list[1]['conn'])
            if msg:
                for client in client_list:
                    # print(1)
                    send(msg, client)
                msg = ''
                send_turn_msg = True
            turn = toggle_turn(turn)

        elif len(player_client_list) == 1:
            if waiting:
                sleep(.5)
                send('waiting', player_client_list[0]['conn'])
                waiting = False
            

if __name__ == "__main__":
    start()
    main()
    pass