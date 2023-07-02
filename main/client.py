import socket
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
from discripts import Port, Addr
from metaclasses import ClientVerifier

CLI_LOG = logging.getLogger('client')

@log
def arg_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', default = DEFAULT_IP, nargs='?') 
    parser.add_argument('-p', default= DEFAULT_PORT, nargs='?')
    parser.add_argument('-n', default=None, nargs='?')
    name_space = parser.parse_args(sys.argv[1:])
    serv_addr = name_space.a
    serv_port = name_space.p
    client_name = name_space.n
    if not client_name:
        client_name = input('Enter the username: ')
    return serv_addr, serv_port, client_name


class Client(metaclass=ClientVerifier):
    port = Port()
    addr = Addr()
    
    def __init__(self, serv_addr, serv_port, client_name):
        self.port = serv_port
        self.addr = serv_addr
        self.client_name = client_name
        self.sock = None

    def init_sock(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Создать сокет TCP
            s.connect((self.addr, self.port)) # Соединиться с сервером
            self.sock = s
            CLI_LOG.info(f'server connection established')
            send_msg(s, self.create_presence())
            serv_answer = self.proc_response_serv_ans(get_msg(self.sock))
            CLI_LOG.info(f'sending message {serv_answer} from server to client')
            print('server connection established')
        except (ValueError, json.JSONDecodeError):  
            CLI_LOG.error(f'invalid message received from client')
            sys.exit(1)
        except (ConnectionAbortedError, ConnectionError, ConnectionResetError):
            CLI_LOG.error(f'the connection to the server {self.addr} was lost')
            sys.exit(1)


    def create_presence(self):
        out = {
            'action' : 'presence',
            'time' : time.time(),
            'user' : {
                'account_name' : self.client_name
            }   
        }
        CLI_LOG.debug(f"generated message 'presence' for user {self.client_name}")
        return out
    
   
    def proc_response_serv_ans(self, data):
        CLI_LOG.debug(f"generated hello_message from the server: {data}")
        if 'response' in data:
            if data['response'] == 200:
                return '200 : OK'
            elif data['response'] == 400:
                raise ValueError(f"400 : {data['error']}")
        ValueError(f'missing response')

   
    def create_exit_msg(self):
        out = {'action' : 'exit',
            'time' : time.time(),
            'account_name' : self.client_name
            }
        return out

      
    def create_msg(self):
        recipient = input('enter the distination of the message: ')
        msg = input('enter message to send: ')

        msg_dict = {
            "action": "message",
            "from" : self.client_name,
            "to" : recipient,
            "time": time.time(),
            "msg_text" : msg
            } 
        CLI_LOG.debug(f"generated dict_message {msg_dict}")
        try:
            send_msg(self.sock, msg_dict)
            CLI_LOG.info(f"on server user {msg_dict['from']} to send {msg_dict['msg_text']} for {msg_dict['to']}")
        except:
            CLI_LOG.critical('Connection with server was lost')
            sys.exit(1)


    def msg_from_server(self):
        while True:
            try:
                msg = get_msg(self.sock)
                if 'action' in msg and msg['action'] == 'message' and 'from' in msg and 'to' in msg \
                and 'msg_text' in msg and msg['to'] == self.client_name:    
                    print(f"\nTo get message from {msg['from']}: {msg['msg_text']}")
                    CLI_LOG.info(f"message received from user {msg['from']}: {msg['msg_text']}")
                else:
                    CLI_LOG.error(f"bad message received from server: {msg}")
                    sys.exit(1)
            except (ValueError, OSError, ConnectionError, ConnectionAbortedError, json.JSONDecodeError):
                CLI_LOG.critical(f"error sending response from server")
                break

  
    def user_interactive(self):
        print(f'You - {self.client_name}')
        print('Command help:')
        print('message - to send message. Enter the recipient and text of the message in the appropriate fields')
        print('exit - exit from the program')
        while True:
            cmd = input('Enter the command: message or exit: ')
            if cmd == 'message':
                self.create_msg()
            elif cmd == 'exit':
                send_msg(self.sock, self.create_exit_msg())
                print('Connection ended.')
                CLI_LOG.info(f"Connection ended after user {self.client_name} command")
                time.sleep(1)
                break
            else:
                print('bad command, try again')

    @property
    def main_loop(self):
        print('Console chat, client modul.')
        self.init_sock()
        receiver = threading.Thread(target=self.msg_from_server, daemon=True)
        receiver.start()
        user_interface = threading.Thread(target=self.user_interactive, daemon=True)
        user_interface.start()
        CLI_LOG.debug(f'The client started processes for sending and receiving messages')
        while True:
            time.sleep(1)
            if receiver.is_alive() and user_interface.is_alive():
                continue
            break


def main():
    serv_addr, serv_port, client_name = arg_parser()       
    client = Client(serv_addr, serv_port, client_name)
    client.main_loop    

        

if __name__ == '__main__':
     main()