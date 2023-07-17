import argparse
import configparser

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt

from server.server_gui import MainWindow
from log.config_server import *
from common.variables import *
from server.core import Server
from common.decos import log
from server.server_db import ServerPool

logger = logging.getLogger('server')


@log
def arg_parser(default_port, default_address):
    '''Парсер аргументов коммандной строки.'''
    logger.debug(f'Запуск парсера аргументов командной строки: {sys.argv}')
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', default=default_port, type=int, nargs='?')
    parser.add_argument('-a', default=default_address, nargs='?')
    namespace = parser.parse_args(sys.argv[1:])
    listen_address = namespace.a
    listen_port = namespace.p
    logger.debug(f'Порт и ip_адрес успешно получены')
    return listen_address, listen_port


def config_load():
    '''Парсер конфигурационного ini файла.'''
    config = configparser.ConfigParser()
    dir_path = os.path.dirname(os.path.realpath(__file__))
    config.read(f"{dir_path}/{'server.ini'}")
    if 'SETTINGS' in config:
        return config
    else:
        config.add_section('SETTINGS')
        config.set('SETTINGS', 'Default_port', str(DEFAULT_PORT))
        config.set('SETTINGS', 'Listen_Address', '')
        config.set('SETTINGS', 'Database_path', '')
        config.set('SETTINGS', 'Database_file', 'server_db.db3')
        return config


def main():
    '''Основная функция'''
    config = config_load()
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
    server_app.setAttribute(Qt.AA_DisableWindowContextHelpButton)
    main_window = MainWindow(database, server, config)
    server_app.exec_()
    server.running = False


if __name__ == '__main__':
    main()
