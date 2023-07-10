import socket
from variables import *
import sys
import json
import time
import argparse
import threading  
sys.path.append('../')
from utils import send_msg, get_msg
import logging
from decos import log
from PyQt5.QtWidgets import QApplication
from client.main_window import UserNameDialog, ClientMainWindow
from metaclasses import ClientVerifier
from client.client_db import ClientPool
from client.transport import ClientTransport


CLI_LOG = logging.getLogger('client')
@log
def arg_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('addr', default=DEFAULT_IP, nargs='?')
    parser.add_argument('port', default=DEFAULT_PORT, type=int, nargs='?')
    parser.add_argument('-n', '--name', default=None, nargs='?')
    namespace = parser.parse_args(sys.argv[1:])
    server_address = namespace.addr
    server_port = namespace.port
    client_name = namespace.name

    if not 1023 < server_port < 65536:
        CLI_LOG.critical(
            f'Попытка запуска клиента с неподходящим номером порта: {server_port}. Допустимы адреса с 1024 до 65535. Клиент завершается.')
        exit(1)

    return server_address, server_port, client_name

if __name__ == '__main__':
    server_address, server_port, client_name = arg_parser()

    client_app = QApplication(sys.argv)
    if not client_name:
        start_dialog = UserNameDialog()
        client_app.exec_()
        if start_dialog.ok_pressed:
            client_name = start_dialog.client_name.text()
            del start_dialog
        else:
            exit(0)
    CLI_LOG.info(
        f'Запущен клиент с парамертами: адрес сервера: {server_address} , порт: {server_port}, имя пользователя: {client_name}')

    database = ClientPool(client_name)
    try:
        transport = ClientTransport(server_port, server_address, database, client_name)
    except ConnectionError:
        exit(1)
    transport.setDaemon(True)
    transport.start()
    main_window = ClientMainWindow(database, transport)
    main_window.make_connection(transport)
    main_window.setWindowTitle(f'Чат Программа alpha release - {client_name}')
    client_app.exec_()
    transport.transport_shutdown()
    transport.join()
