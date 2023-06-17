from socket import *
from variables import *
import sys
import json
import time
import argparse
import threading  
sys.path.append('../')
from main.utils import send_msg, get_msg
import logging
import log.config_client
from decos import log

CLI_LOG = logging.getLogger('client')

@log
def create_msg(sock:socket, account_name='Guest'):
    recipient = input('enter the distination of the message: ')
    msg = input('enter message to send: ')

    msg_dict = {
        "action": "message",
        "from" : account_name,
        "to" : recipient,
        "time": time.time(),
        "msg_text" : msg
        } 
    
    CLI_LOG.debug(f"generated dict_message {msg_dict}")
    try:
        send_msg(sock, msg_dict)
        CLI_LOG.info(f"on server user {msg_dict['from']} to send {msg_dict['msg_text']} for {msg_dict['to']}")
    except:
        CLI_LOG.critical('Connection with server was lost')
        sys.exit(1)


@log
def msg_from_server(sock, data):
    while True:
        try:
            msg = get_msg(sock)
            if 'action' in msg and msg['action'] == 'message' and 'from' in msg and 'to' in msg \
            and 'msg_text' in msg and msg['to'] == data:    
                print(f"\nTo get message from {msg['from']}: {msg['msg_text']}")
                CLI_LOG.info(f"message received from user {msg['from']}: {msg['msg_text']}")
            else:
                CLI_LOG.error(f"bad message received from server: {msg}")
                sys.exit(1)
        except (ValueError, OSError, ConnectionError, ConnectionAbortedError, json.JSONDecodeError):
            CLI_LOG.critical(f"error sending response from server")
            break

    

@log
def create_presence(account_name):
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
    parser.add_argument('-n', '--name', default=None, nargs='?')
    name_space = parser.parse_args(sys.argv[1:])
    serv_addr = name_space.addr
    serv_port = name_space.port
    client_name = name_space.name
    if not 1023 < serv_port < 65536:
        CLI_LOG.critical(f"launch attempt starting client on an invalid {serv_port} port")
        sys.exit(1)
    return serv_addr, serv_port, client_name

@log
def create_exit_msg(user_name):
    out = {'action' : 'exit',
           'time' : time.time(),
           'account_name' : user_name   
        }
    return out

@log
def print_help():
    print('Command help:')
    print('message - to send message. Enter the recipient and text of the message in the appropriate fields')
    print('exit - exit from the program')

@log
def user_interactive(sock, user_name):
    print(f'You - {user_name}')
    print_help()
    while True:
        cmd = input('Enter the command: message or exit: ')
        if cmd == 'message':
            create_msg(sock, user_name)
        elif cmd == 'exit':
            send_msg(sock, create_exit_msg(user_name))
            print('Connection ended.')
            CLI_LOG.info(f"Connection ended after user {user_name} command")
            time.sleep(1)
            break
        else:
            print('bad command, try again')

        


def main():
    print('Console chat, client modul.')
    serv_addr, serv_port, client_name = arg_parser()
    if not client_name:
        client_name = input('Enter the username: ')
    CLI_LOG.info(f"started client socket with parameters: addres server{serv_addr}, port {serv_port}, working mode {client_name}")

    try:
        s = socket(AF_INET, SOCK_STREAM) # Создать сокет TCP
        s.connect((serv_addr, serv_port)) # Соединиться с сервером
        CLI_LOG.info(f'server connection established')
        send_msg(s, create_presence(client_name))
        serv_answer = proc_response_serv_ans(get_msg(s))
        CLI_LOG.info(f'sending message {serv_answer} from server to client')
        print('server connection established')
    except (ValueError, json.JSONDecodeError):  
        CLI_LOG.error(f'invalid message received from client')
        sys.exit(1)
    except (ConnectionAbortedError, ConnectionError, ConnectionResetError):
        CLI_LOG.error(f'the connection to the server {serv_addr} was lost')
        sys.exit(1)
    else:
        data = (s, client_name)
        receiver = threading.Thread(target=msg_from_server, args=data, daemon=True)
        receiver.start()
        user_interface = threading.Thread(target=user_interactive, args=data, daemon=True)
        user_interface.start()
        CLI_LOG.debug(f'The client started processes for sending and receiving messages')
        while True:
            time.sleep(1)
            if receiver.is_alive() and user_interface.is_alive():
                continue
            break

        

        

if __name__ == '__main__':
     main()