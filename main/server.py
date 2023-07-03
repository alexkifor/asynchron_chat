import socket
import select
import sys
import argparse
import time
import threading
sys.path.append('../')
from main.utils import send_msg, get_msg
from main.variables import *
import logging
import log.config_server
from decos import log
from discripts import Port, Addr
from metaclasses import ServerVerifier
from server_db import ServerPool


SERV_LOG = logging.getLogger('server')

@log
def arg_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', default = '', nargs='?') 
    parser.add_argument('-p', default= DEFAULT_PORT, type=int, nargs='?')
    name_space = parser.parse_args(sys.argv[1:])
    serv_addr = name_space.a
    serv_port = name_space.p
    return serv_addr, serv_port


class Server(threading.Thread, metaclass=ServerVerifier):
    port = Port()
    addr = Addr()

    def __init__(self, serv_addr, serv_port, database):
        self.addr = serv_addr
        self.port = serv_port
        self.database = database
        self.clients = []
        self.messages = []
        self.names = dict()
        super().__init__()
        
    def init_socket(self):
        SERV_LOG.info(f"trying to start socket from on the server")
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((self.addr, self.port))
        s.settimeout(0.5)
        self.sock = s
        self.sock.listen()
        SERV_LOG.info(f"server socket waiting for connection on {self.port} port with ip address: {self.addr}."
                      f"If ip_address is not soecified, server waiting for connection on {self.port} from any ip address")

    def run(self):
        self.init_socket()
        while True:
            try:
                client, client_addr = self.sock.accept()
            except OSError:
                pass
            else:
                SERV_LOG.info(f"connection server with {client_addr}")
                self.clients.append(client)
            rec_cli_lst = []
            send_cli_lst = []
            err_lst = []
        
            try:
                if self.clients:
                    rec_cli_lst, send_cli_lst, err_lst = select.select(self.clients, self.clients, [], 0)
            except OSError:
                pass

            if rec_cli_lst:
                for client in rec_cli_lst:
                    try:
                        self.handler_client_msg(get_msg(client), client)
                    except:
                        SERV_LOG.info(f"client {client.getpeername()} disconnected from the server")
                        self.clients.remove(client)
            for msg in self.messages:
                try:
                    self.proc_msg_to_client(msg, send_cli_lst)
                except:
                    SERV_LOG.info(f"Connection with user {msg['to']} was lost")
                    self.clients.remove(self.names[msg['to']])
                    del self.names[msg['to']]
            self.messages.clear()

    
    def proc_msg_to_client(self, msg, cli_sock):
        if msg['to'] in self.names and self.names[msg['to']] in cli_sock:
            send_msg(self.names[msg['to']], msg)
            SERV_LOG.info(f"message sent to user {msg['to']} from user {msg['from']}")
        elif msg['to'] in self.names and self.names[msg['from']] not in cli_sock:
            raise ConnectionError
        else:
            SERV_LOG.error(f"user {msg['to']} not register on the server, sending message is not imposible")

        
    def handler_client_msg(self, data, client):
        '''
        Функция обрабатывает сообщения от клиента и выдает ответ в виде словаря
        :param data:
        :return:
        '''
        SERV_LOG.debug(f'parsig message from client {data}')
        if 'action' in data and data['action'] == 'presence' and 'time' in data \
            and 'user' in data:
                if data['user']['account_name'] not in self.names.keys():
                    self.names[data['user']['account_name']] = client
                    client_ip, client_port = client.getpeername()
                    self.database.user_login(data['user']['account_name'], client_ip, client_port)
                    send_msg(client, {'response': 200})
                else:
                    send_msg(client, {
                        'response': 400,
                        'error': 'Name already in use'
                        })
                    self.clients.remove(client)
                    client.close()
                return
        elif 'action' in data and data['action'] == 'message' and 'to' in data and 'time' in data \
            and 'from' in data and 'msg_text' in data:
            self.messages.append(data)
            return
        elif 'action' in data and data['action'] == 'exit' and 'account_name' in data:
            self.database.user_logout(data['account_name'])
            self.clients.remove(self.names[data['account_name']])
            self.names[data['account_name']].close()
            del self.names[data['account_name']]
            return
        else:
            send_msg(client, {
                'response': 400,
                'error': 'Incorrect response'
            })
            return 

def print_help():
    print('Commands: ')
    print('users - list all users')
    print('connected - list all active users')
    print('loghist - login history user')
    print('exit - shutdown server')
    print('help - command helper')       


def main():
    '''
    Функция загружает параметры из командной строки, 
    если параметров нет задает параметры по умолчанию . Создает сокет
    и прослушивает указанный адрес.
    '''
    serv_addr, serv_port = arg_parser()
    database = ServerPool()
    server = Server(serv_addr, serv_port, database)
    server.daemon = True
    server.start()
    print_help()
    while True:
        cmd = input('enter command: ')
        if cmd == 'help':
            print_help()
        elif cmd == 'exit':
            break
        elif cmd == 'users':
            for user in sorted(database.users_list()):
                print(f"user {user[0]}, last login {user[1]}")
        elif cmd == 'connected':
            for user in sorted(database.active_users_list()):
                print(f"user {user[0]}, connected: {user[1]}:{user[2]}, connected time: {user[3]}")
        elif cmd == 'loghist':
            name = input('enter user name to look his login history or press "Enter" to lokk all history: ')
            for user in sorted(database.login_history(name)):
                print(f"user: {user[0]}, login time: {user[1]}. Enter with: {user[2]:{user[3]}}")
        else:
            print('Enter bad command')


    


if __name__ == '__main__':
     main()


