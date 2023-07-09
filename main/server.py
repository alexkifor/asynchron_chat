import socket
import select
import sys
import os
import argparse
import time
import threading
import configparser
sys.path.append('../')
from main.utils import send_msg, get_msg
from main.variables import *
import logging
import log.config_server
from decos import log
from discripts import Port, Addr
from metaclasses import ServerVerifier
from server_db import ServerPool
from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtCore import QTimer
from server_gui import MainWindow, gui_create_model, HistoryWindow, create_stat_model, ConfigWindow
# from PyQt5.QtGui import QStandardItemModel, QStandardItemv


SERV_LOG = logging.getLogger('server')

new_connection = False
conflag_lock = threading.Lock()

@log
def arg_parser(default_port, default_address):
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', default=default_port, type=int, nargs='?')
    parser.add_argument('-a', default=default_address, nargs='?')
    namespace = parser.parse_args(sys.argv[1:])
    listen_address = namespace.a
    listen_port = namespace.p
    return listen_address, listen_port

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
                        for name in self.names:
                            if self.names[name] == client:
                                self.database.user_logout(name)
                                del self.names[name]
                                break
                        self.clients.remove(client)
            for msg in self.messages:
                try:
                    self.proc_msg_to_client(msg, send_cli_lst)
                except:
                    SERV_LOG.info(f"Connection with user {msg['to']} was lost")
                    self.clients.remove(self.names[msg['to']])
                    self.database.user_logout(msg['to'])
                    del self.names[msg['to']]
            self.messages.clear()

    
    def proc_msg_to_client(self, msg, cli_sock):
        if msg['to'] in self.names and self.names[msg['to']] in cli_sock:
            send_msg(self.names[msg['to']], msg)
            SERV_LOG.info(f"message sent to user {msg['to']} from user {msg['from']}")
        elif msg['to'] in self.names and self.names[msg['to']] not in cli_sock:
            raise ConnectionError
        else:
            SERV_LOG.error(f"user {msg['to']} not register on the server, sending message is not imposible")

        
    def handler_client_msg(self, data, client):
        '''
        Функция обрабатывает сообщения от клиента и выдает ответ в виде словаря
        :param data:
        :return:
        '''
        global new_connection
        SERV_LOG.debug(f'parsig message from client {data}')
        if 'action' in data and data['action'] == 'presence' and 'time' in data \
            and 'user' in data:
                if data['user']['account_name'] not in self.names.keys():
                    self.names[data['user']['account_name']] = client
                    client_ip, client_port = client.getpeername()
                    self.database.user_login(data['user']['account_name'], client_ip, client_port)
                    send_msg(client, {'response': 200})
                    with conflag_lock:
                        new_connection = True
                else:
                    send_msg(client, {
                        'response': 400,
                        'error': 'Name already in use'
                        })
                    self.clients.remove(client)
                    client.close()
                return
        elif 'action' in data and data['action'] == 'message' and 'to' in data and 'time' in data \
            and 'from' in data and 'msg_text' in data and self.names[data['from'] == client]:
            self.messages.append(data)
            self.database.process_message(data['from'], data['to'])
            return
        elif 'action' in data and data['action'] == 'exit' and 'account_name' in data and \
            self.names[data['account_name']] == client:
            self.database.user_logout(data['account_name'])
            SERV_LOG.info(f"User {data['account_name']} correctly disconnected from the server")
            self.clients.remove(self.names[data['account_name']])
            self.names[data['account_name']].close()
            del self.names[data['account_name']]
            with conflag_lock:
                new_connection = True
            return
        elif 'action' in data and data['action'] == 'get_contacts' and 'user' in data and \
            self.names[data['user']] == client:
            response = {'response': 202,
                        'data_list': self.database.get_contacts(data['user'])}
            send_msg(client, response)
        elif 'action' in data and data['action'] == 'add' and 'account_name' in data and 'user' in data \
            and self.names[data['user']] == client:
            self.database.add_contact(data['user'], data['account_name'])
            send_msg(client, {'response': 200})
        elif 'action' in data and data['action'] == 'remove' and 'account_name' in data and 'user' in data \
            and self.names[data['user']] == client:
            self.database.remove_contact(data['user'], data['account_name'])
            send_msg(client, {'response': 200})
        elif 'action' in data and data['action'] == 'get_users' and 'account_name' in data \
            and self.names[data['account_name']] == client:
            response = {'response': 202,
                        'data_list': [user[0] for user in self.database.users_list()]}
            send_msg(client, response)
        else:
            send_msg(client, {
                'response': 400,
                'error': 'Incorrect response'
            })
            return 
 
def main():
    config = configparser.ConfigParser()

    dir_path = os.path.dirname(os.path.realpath(__file__))
    config.read(f"{dir_path}/{'server.ini'}")


    listen_address, listen_port = arg_parser(
        config['SETTINGS']['Default_port'], config['SETTINGS']['Listen_Address'])

 
    database = ServerPool(
        os.path.join(
            config['SETTINGS']['Database_path'],
            config['SETTINGS']['Database_file']))

   
    server = Server(listen_address, listen_port, database)
    server.daemon = True
    server.start()
    server_app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.statusBar().showMessage('Server Working')
    main_window.active_clients_table.setModel(gui_create_model(database))
    main_window.active_clients_table.resizeColumnsToContents()
    main_window.active_clients_table.resizeRowsToContents()

    
    def list_update():
        global new_connection
        if new_connection:
            main_window.active_clients_table.setModel(
                gui_create_model(database))
            main_window.active_clients_table.resizeColumnsToContents()
            main_window.active_clients_table.resizeRowsToContents()
            with conflag_lock:
                new_connection = False

    
    def show_statistics():
        global stat_window
        stat_window = HistoryWindow()
        stat_window.history_table.setModel(create_stat_model(database))
        stat_window.history_table.resizeColumnsToContents()
        stat_window.history_table.resizeRowsToContents()
        stat_window.show()


    def server_config():
        global config_window
        config_window = ConfigWindow()
        config_window.db_path.insert(config['SETTINGS']['Database_path'])
        config_window.db_file.insert(config['SETTINGS']['Database_file'])
        config_window.port.insert(config['SETTINGS']['Default_port'])
        config_window.ip.insert(config['SETTINGS']['Listen_Address'])
        config_window.save_btn.clicked.connect(save_server_config)

    
    def save_server_config():
        global config_window
        message = QMessageBox()
        config['SETTINGS']['Database_path'] = config_window.db_path.text()
        config['SETTINGS']['Database_file'] = config_window.db_file.text()
        try:
            port = int(config_window.port.text())
        except ValueError:
            message.warning(config_window, 'Ошибка', 'Порт должен быть числом')
        else:
            config['SETTINGS']['Listen_Address'] = config_window.ip.text()
            if 1023 < port < 65536:
                config['SETTINGS']['Default_port'] = str(port)
                print(port)
                with open('server.ini', 'w') as conf:
                    config.write(conf)
                    message.information(
                        config_window, 'OK', 'Настройки успешно сохранены!')
            else:
                message.warning(
                    config_window,
                    'Ошибка',
                    'Порт должен быть от 1024 до 65536')

    timer = QTimer()
    timer.timeout.connect(list_update)
    timer.start(1000)
    main_window.refresh_button.triggered.connect(list_update)
    main_window.show_history_button.triggered.connect(show_statistics)
    main_window.config_btn.triggered.connect(server_config)
    server_app.exec_()


if __name__ == '__main__':
    main()