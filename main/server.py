import socket
import select
import sys
import argparse
import time
sys.path.append('../')
from main.utils import send_msg, get_msg
from main.variables import *
import logging
import log.config_server
from decos import log
from discripts import Port, Addr
from metaclasses import ServerVerifier


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


class Server(metaclass=ServerVerifier):
    port = Port()
    addr = Addr()

    def __init__(self, serv_addr, serv_port):
        self.addr = serv_addr
        self.port = serv_port
        self.clients = []
        self.messages = []
        self.names = dict()
        
    def init_socket(self):
        SERV_LOG.info(f"trying to start socket from on the server")
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((self.addr, self.port))
        s.settimeout(0.5)
        self.sock = s
        self.sock.listen()
        SERV_LOG.info(f"server socket waiting for connection on {self.port} port with ip address: {self.addr}."
                      f"If ip_address is not soecified, server waiting for connection on {self.port} from any ip address")

    @property
    def main_loop(self):
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

    
    def proc_msg_to_client(self,msg, cli_sock):
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

def main():
    '''
    Функция загружает параметры из командной строки, 
    если параметров нет задает параметры по умолчанию . Создает сокет
    и прослушивает указанный адрес.
    '''
    serv_addr, serv_port = arg_parser()
    server = Server(serv_addr, serv_port)
    server.main_loop

  
    


if __name__ == '__main__':
     main()


