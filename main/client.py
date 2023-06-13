from socket import *
from variables import *
import sys
import json
import time
import argparse
sys.path.append('../')
from main.utils import send_msg, get_msg
import logging
import log.config_client
from decos import log

CLI_LOG = logging.getLogger('client')

@log
def create_msg(sock:socket, account_name="Guest"):
    msg = input('enter message to send or !!! to complete: ')
    if msg == '!!!':
        sock.close()
        CLI_LOG.info(f"shutdown by user {account_name} command")
        print('Goodbuy')
        sys.exit(0)

    msg_dict = {
        "action": "message",
        "time": time.time(),
        "account_name": account_name,
        "msg_text" : msg
        } 
    
    CLI_LOG.debug(f"generated dict_message {msg} to send the server from {account_name}")
    return msg_dict



@log
def msg_from_server(data):
    if 'action' in data and data['action'] == 'message' and 'sender' in data and 'msg_text' in data :    
        print(f"message received from user {data['sender']}: {data['msg_text']}")
        CLI_LOG.info(f"message received from user {data['sender']}: {data['msg_text']}")
    else:
        CLI_LOG.error(f"bad message received from server: {data}")
        sys.exit(1)
    

@log
def create_presence(account_name='Guest'):
    out = {
        'action' : 'presence',
        'time' : time.time(),
        'user' : {
            'account_name' : account_name
        }   
    }
    CLI_LOG.debug(f"generated message 'presence' for user {account_name}")
    return out

@log
def proc_response_serv_ans(data):
    CLI_LOG.debug(f"generated hello_message from the server: {data}")
    if 'response' in data:
        if data['response'] == 200:
            return '200 : OK'
        elif data['response'] == 400:
            raise ValueError(f"400 : {data['error']}")
    ValueError(f'missing response')

@log
def arg_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('addr', default = DEFAULT_IP, nargs='?') 
    parser.add_argument('port', default= DEFAULT_PORT, nargs='?')
    parser.add_argument('-m', '--mode', default='listen', nargs='?')
    name_space = parser.parse_args(sys.argv[1:])
    serv_addr = name_space.addr
    serv_port = name_space.port
    client_mode = name_space.mode
    if not 1023 < serv_port < 65536:
        CLI_LOG.critical(f"launch attempt starting client on an invalid {serv_port} port")
        sys.exit(1)
    if client_mode not in ('listen', 'send'):
        CLI_LOG.critical(f"specifide invalid {client_mode} mode")
        sys.exit(1)
    return serv_addr, serv_port, client_mode




def main():
    serv_addr, serv_port, client_mode = arg_parser()
    CLI_LOG.info(f"started client socket with parameters: addres server{serv_addr}, port {serv_port}, working mode {client_mode}")

    try:
        s = socket(AF_INET, SOCK_STREAM) # Создать сокет TCP
        s.connect((serv_addr, serv_port)) # Соединиться с сервером
        CLI_LOG.info(f'server connection established')
        send_msg(s, create_presence())
        serv_answer = proc_response_serv_ans(get_msg(s))
        CLI_LOG.info(f'sending message {serv_answer} from server to client')
        print('server connection established')
    except (ValueError, json.JSONDecodeError):  
        CLI_LOG.error(f'invalid message received from client')
        sys.exit(1)
    else:
        if client_mode == 'send':
            print('the client is in message sending mode')
        else:
            print('the client is in receive mode')
        while True:
            if client_mode == 'send':
                try:
                    send_msg(s, create_msg(s))
                except(ConnectionAbortedError, ConnectionError, ConnectionResetError):
                    CLI_LOG.error(f'the connection to the server {serv_addr} was lost')
                    sys.exit(1)
            if client_mode == 'listen':
                try:
                    msg_from_server(get_msg(s))
                except(ConnectionAbortedError, ConnectionError, ConnectionResetError):
                    CLI_LOG.error(f'the connection to the server {serv_addr} was lost')
                    sys.exit(1)


        

if __name__ == '__main__':
     main()