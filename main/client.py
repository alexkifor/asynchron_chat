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
from clcient_db import ClientPool




CLI_LOG = logging.getLogger('client')
sock_lock = threading.Lock()
database_lock = threading.Lock()
class ClientSender(threading.Thread, metaclass=ClientVerifier):
    def __init__(self, account_name, sock, database):
        self.account_name = account_name
        self.sock = sock
        self.database = database
        super().__init__()

    def create_exit_message(self):
        return {
            'action': 'exit',    
            'time': time.time(),
            'account_name': self.account_name
        }

    def create_message(self):
        to = input('Введите получателя сообщения: ')
        message = input('Введите сообщение для отправки: ')

        with database_lock:
            if not self.database.check_user(to):
                CLI_LOG.error(f'Попытка отправить сообщение незарегистрированому получателю: {to}')
                return

        message_dict = {
            'action': 'message',
            'from': self.account_name,
            'to': to,
            'time': time.time(),
            'msg_text': message
        }
        CLI_LOG.debug(f'Сформирован словарь сообщения: {message_dict}')

        with database_lock:
            self.database.save_message(self.account_name , to , message)

        with sock_lock:
            try:
                send_msg(self.sock, message_dict)
                CLI_LOG.info(f'Отправлено сообщение для пользователя {to}')
            except OSError as err:
                if err.errno:
                    CLI_LOG.critical('Потеряно соединение с сервером.')
                    exit(1)
                else:
                    CLI_LOG.error('Не удалось передать сообщение. Таймаут соединения')

    def run(self):
        self.print_help()
        while True:
            command = input('Введите команду: ')
            if command == 'message':
                self.create_message()
            elif command == 'help':
                self.print_help()
            elif command == 'exit':
                with sock_lock:
                    try:
                        send_msg(self.sock, self.create_exit_message())
                    except:
                        pass
                    print('Завершение соединения.')
                    CLI_LOG.info('Завершение работы по команде пользователя.')
                time.sleep(0.5)
                break

            elif command == 'contacts':
                with database_lock:
                    contacts_list = self.database.get_contacts()
                for contact in contacts_list:
                    print(contact)

            elif command == 'edit':
                self.edit_contacts()

            elif command == 'history':
                self.print_history()

            else:
                print('Команда не распознана, попробойте снова. help - вывести поддерживаемые команды.')

    def print_help(self):
        print('Поддерживаемые команды:')
        print('message - отправить сообщение. Кому и текст будет запрошены отдельно.')
        print('history - история сообщений')
        print('contacts - список контактов')
        print('edit - редактирование списка контактов')
        print('help - вывести подсказки по командам')
        print('exit - выход из программы')

    def print_history(self):
        ask = input('Показать входящие сообщения - in, исходящие - out, все - просто Enter: ')
        with database_lock:
            if ask == 'in':
                history_list = self.database.get_history(to_who=self.account_name)
                for message in history_list:
                    print(f'\nСообщение от пользователя: {message[0]} от {message[3]}:\n{message[2]}')
            elif ask == 'out':
                history_list = self.database.get_history(from_who=self.account_name)
                for message in history_list:
                    print(f'\nСообщение пользователю: {message[1]} от {message[3]}:\n{message[2]}')
            else:
                history_list = self.database.get_history()
                for message in history_list:
                    print(f'\nСообщение от пользователя: {message[0]}, пользователю {message[1]} от {message[3]}\n{message[2]}')

    
    def edit_contacts(self):
        ans = input('Для удаления введите del, для добавления add: ')
        if ans == 'del':
            edit = input('Введите имя удаляемного контакта: ')
            with database_lock:
                if self.database.check_contact(edit):
                    self.database.del_contact(edit)
                else:
                    CLI_LOG.error('Попытка удаления несуществующего контакта.')
        elif ans == 'add':
            edit = input('Введите имя создаваемого контакта: ')
            if self.database.check_user(edit):
                with database_lock:
                    self.database.add_contact(edit)
                with sock_lock:
                    try:
                        add_contact(self.sock , self.account_name, edit)
                    except ConnectionError:
                        CLI_LOG.error('Не удалось отправить информацию на сервер.')


class ClientReader(threading.Thread, metaclass=ClientVerifier):
    def __init__(self, account_name, sock, database):
        self.account_name = account_name
        self.sock = sock
        self.database = database
        super().__init__()

    def run(self):
        while True:
            time.sleep(1)
            with sock_lock:
                try:
                    message = get_msg(self.sock)

                except UnicodeDecodeError:
                    CLI_LOG.error(f'Не удалось декодировать полученное сообщение.')
                except OSError as err:
                    if err.errno:
                        CLI_LOG.critical(f'Потеряно соединение с сервером.')
                        break
        
                except (ConnectionError, ConnectionAbortedError, ConnectionResetError, json.JSONDecodeError):
                    CLI_LOG.critical(f'Потеряно соединение с сервером.')
                    break
                else:
                    if 'action' in message and message['action'] == 'message' and 'from' in message and 'to' in message \
                            and 'msg_text' in message and message['to'] == self.account_name:
                        print(f"\nПолучено сообщение от пользователя {message['from']}:\n{message['msg_text']}")
                        with database_lock:
                            try:
                                self.database.save_message(message['from'], self.account_name, message['msg_text'])
                            except:
                                CLI_LOG.error('Ошибка взаимодействия с базой данных')

                        CLI_LOG.info(f"Получено сообщение от пользователя {message['from']}:\n{message['msg_text']}")
                    else:
                        CLI_LOG.error(f'Получено некорректное сообщение с сервера: {message}')


@log
def create_presence(account_name):
    out = {
        'action': 'presence',
        'time': time.time(),
        'user': {
            'account_name': account_name
        }
    }
    CLI_LOG.debug(f'Сформировано "presence" сообщение для пользователя {account_name}')
    return out


@log
def process_response_ans(message):
    CLI_LOG.debug(f'Разбор приветственного сообщения от сервера: {message}')
    if 'response' in message:
        if message['response'] == 200:
            return '200 : OK'
        elif message['response'] == 400:
            raise ConnectionError(f"400 : {message['error']}")
    raise Exception('response')


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

def contacts_list_request(sock, name):
    CLI_LOG.debug(f'Запрос контакт листа для пользователся {name}')
    req = {
        'action': 'get_contacts',
        'time': time.time(),
        'user': name
    }
    CLI_LOG.debug(f'Сформирован запрос {req}')
    send_msg(sock, req)
    ans = get_msg(sock)
    CLI_LOG.debug(f'Получен ответ {ans}')
    if 'response' in ans and ans['response'] == 202:
        return ans['data_list']
    else:
        raise ConnectionError


def add_contact(sock, username, contact):
    CLI_LOG.debug(f'Создание контакта {contact}')
    req = {
        'action': 'add',
        'time': time.time(),
        'user': username,
        'account_name': contact
    }
    send_msg(sock, req)
    ans = get_msg(sock)
    if 'response' in ans and ans['response'] == 200:
        pass
    else:
        raise Exception('Ошибка создания контакта')
    print('Удачное создание контакта.')


def user_list_request(sock, username):
    CLI_LOG.debug(f'Запрос списка известных пользователей {username}')
    req = {
        'action': 'get_users',
        'time': time.time(),
        'account)name': username
    }
    send_msg(sock, req)
    ans = get_msg(sock)
    if 'response' in ans and ans['response'] == 202:
        return ans['data_list']
    else:
        raise ConnectionError


def remove_contact(sock, username, contact):
    CLI_LOG.debug(f'Создание контакта {contact}')
    req = {
        'action': 'remove',
        'time': time.time(),
        'user': username,
        'account_name': contact
    }
    send_msg(sock, req)
    ans = get_msg(sock)
    if 'response' in ans and ans['response'] == 200:
        pass
    else:
        raise Exception('Ошибка удаления клиента')
    print('Удачное удаление')


def database_load(sock, database, username):
    try:
        users_list = user_list_request(sock, username)
    except ConnectionError:
        CLI_LOG.error('Ошибка запроса списка известных пользователей.')
    else:
        database.add_users(users_list)

    try:
        contacts_list = contacts_list_request(sock, username)
    except Exception:
        CLI_LOG.error('Ошибка запроса списка контактов.')
    else:
        for contact in contacts_list:
            database.add_contact(contact)


def main():
    print('Консольный месседжер. Клиентский модуль')
    server_address, server_port, client_name = arg_parser()
    if not client_name:
        client_name = input('Введите имя пользователя: ')
    else:
        print(f'Клиентский модуль запущен с именем: {client_name}')

    CLI_LOG.info(
        f'Запущен клиент с парамертами: адрес сервера: {server_address} , порт: {server_port}, имя пользователя: {client_name}')

    try:
        transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        transport.settimeout(1)

        transport.connect((server_address, server_port))
        send_msg(transport, create_presence(client_name))
        answer = process_response_ans(get_msg(transport))
        CLI_LOG.info(f'Установлено соединение с сервером. Ответ сервера: {answer}')
        print(f'Установлено соединение с сервером.')
    except json.JSONDecodeError:
        CLI_LOG.error('Не удалось декодировать полученную Json строку.')
        exit(1)
    except (ConnectionRefusedError, ConnectionError):
        CLI_LOG.critical(
            f'Не удалось подключиться к серверу {server_address}:{server_port}, конечный компьютер отверг запрос на подключение.')
        exit(1)
    else:

        database = ClientPool(client_name)
        database_load(transport, database, client_name)
        module_sender = ClientSender(client_name, transport, database)
        module_sender.daemon = True
        module_sender.start()
        CLI_LOG.debug('Запущены процессы')
        module_receiver = ClientReader(client_name, transport, database)
        module_receiver.daemon = True
        module_receiver.start()

        while True:
            time.sleep(1)
            if module_receiver.is_alive() and module_sender.is_alive():
                continue
            break


if __name__ == '__main__':
    main()
