import socket
import threading
from time import sleep

HEADER = 64
FORMAT = 'utf-8'
PORT = 6061
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
    return msg

def handle_client(conn, addr):
    print(f'[NEW CONNECTION] {addr} conneted')
    connected = True
    w_turn = True
    test = True
    send_turn_msg = True
    msg = ''
    first_black_case = True
    while connected:
        if len(player_client_list) == 2:
            if w_turn:
                if send_turn_msg:
                    for client in player_client_list:
                        send('white', client['conn'])
                    print('white')
                    send_turn_msg = False
                if (conn == player_client_list[0]['conn'] and addr == player_client_list[0]['addr'] and player_client_list[0]['player_piece'] == 'white'): 
                    msg = recv(conn)
                    if msg:
                        if msg == DISCONNECT_MSG:
                            connected = False
                        print(f'{addr[1]}: {msg}')
                w_turn = False
            else:
                if send_turn_msg:
                    for client in player_client_list:
                        send('black', client['conn'])
                    print('black')
                    send_turn_msg = False
                if (conn == player_client_list[1]['conn'] and addr == player_client_list[1]['addr'] and player_client_list[1]['player_piece'] == 'black'):   
                    print('yay')
                    msg = recv(conn)
                    if msg:
                        if msg == DISCONNECT_MSG:
                            connected = False
                        print(f'{addr[1]}: {msg}')
                w_turn = True
            if not send_turn_msg and msg:
                if (msg or (conn == player_client_list[1]['conn'] and addr == player_client_list[1]['addr'] and first_black_case)): 
                    print('sdf')       
                    for client in client_list:
                        send(msg, client)
                    send_turn_msg = True
                    msg = ''
                    first_black_case = False
            
        else:
            if test:
                send('waiting', conn)
                test = False
        
    conn.close()

def start():
    print('[STARTING] server is starting...')
    server.listen() 
    print(f'[LISTENING] server is listening at {SERVER}')
    while True:
        conn, addr = server.accept()
        client_list.append(conn)
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
        client_thread = threading.Thread(target=handle_client, args=(conn, addr))
        client_thread.start()
        #print(f'[ACTIVE CONNECTIONS] {threading.activeCount()-1}')
        print(player_client_list)

if __name__ == "__main__":
    start()
    pass