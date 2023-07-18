import json
import socket
import sys
import select
import threading

import hmac
import binascii

sys.path.append('../../')
from main.log.config_server import *
from main.common.utils import *
from main.common.decos import login_required
from main.common.discripts import Port, Addr
from main.common.metaclasses import ServerVerifier


logger = logging.getLogger('server')


class Server(threading.Thread):
    '''
    Основной класс сервера. Принимает содинения, словари - пакеты
    от клиентов, обрабатывает поступающие сообщения.
    Работает в качестве отдельного потока.
    '''

    port = Port()
    addr = Addr()

    def __init__(self, listen_address, listen_port, database):
        self.addr = listen_address
        self.port = listen_port
        self.database = database
        self.sock = None
        self.clients = []
        self.listen_sock = None
        self.error_sock = None
        self.running = True
        self.names = dict()
        super().__init__()

    def init_socket(self):
        '''Метод инициализатор сокета.'''
        logger.info(
            f'Запущен сервер, порт для подключений: {self.port} , адрес с которого принимаются подключения: \
            {self.addr}.Если адрес не указан, принимаются соединения с любых адресов.')
        transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        transport.bind((self.addr, self.port))
        transport.settimeout(0.5)
        self.sock = transport
        self.sock.listen(MAX_CONNECT)

    def run(self):
        '''Метод основной цикл потока.'''
        self.init_socket()
        while self.running:
            try:
                client, client_address = self.sock.accept()
            except OSError:
                pass
            else:
                logger.info(f'Установлено соедение с ПК {client_address}')
                client.settimeout(5)
                self.clients.append(client)

            recv_data_lst = []
            send_data_lst = []
            err_lst = []
            try:
                if self.clients:
                    recv_data_lst, self.listen_sock, self.error_sock = select.select(
                        self.clients, self.clients, [], 0)
            except OSError as err:
                logger.error(f'Ошибка работы с сокетами: {err.errno}')

            if recv_data_lst:
                for client_with_message in recv_data_lst:
                    try:
                        self.process_client_message(
                            get_msg(client_with_message), client_with_message)
                    except (OSError, json.JSONDecodeError, TypeError) as err:
                        logger.debug(
                            f'Получены данные из клиентского исключения.',
                            exc_info=err)
                        self.remove_client(client_with_message)

    def remove_client(self, client):
        '''
        Метод обработчик клиента с которым прервана связь.
        Ищет клиента и удаляет его из списков и базы:
        '''
        logger.info(f'Клиент {client.getpeername()} отключился от сервера.')
        for name in self.names:
            if self.names[name] == client:
                self.database.user_logout(name)
                del self.names[name]
                break
        self.clients.remove(client)
        client.close()

    def process_message(self, message):
        '''Метод отправки сообщения клиенту.'''
        if message[DESTINATION] in self.names and self.names[message[DESTINATION]
                                                             ] in self.listen_sock:
            try:
                send_msg(self.names[message[DESTINATION]], message)
                logger.info(
                    f'Отправлено сообщение пользователю {message[DESTINATION]} \
                 от пользователя {message[SENDER]}.')
            except OSError:
                self.remove_client(message[DESTINATION])
        elif message[DESTINATION] in self.names and self.names[message[DESTINATION]] not in self.listen_sock:
            logger.error(
                f'Coeдинение с клиентом {message[DESTINATION]} была потеряна. \
             Соединение закрыто, отправка сообщения невозможна.')
            self.remove_client(self.names[message[DESTINATION]])
        else:
            logger.error(
                f'Пользователь {message[DESTINATION]} не зарегистрирован на сервере, отправка сообщения невозможна.')

    @login_required
    def process_client_message(self, message, client):
        '''Метод отбработчик поступающих сообщений.'''
        logger.debug(f'Разбор сообщения от клиента : {message}')
        if ACTION in message and message[ACTION] == PRESENCE and TIME in message and USER in message:
            self.autorize_user(message, client)
        elif ACTION in message and message[ACTION] == MESSAGE and DESTINATION in message and TIME in message \
                and SENDER in message and MESSAGE_TEXT in message and self.names[message[SENDER]] == client:
            if message[DESTINATION] in self.names:
                self.database.process_message(
                    message[SENDER], message[DESTINATION])
                self.process_message(message)
                try:
                    send_msg(client, RESPONSE_200)
                except OSError:
                    self.remove_client(client)
            else:
                response = RESPONSE_400
                response[ERROR] = 'Пользователь не зарегистрирован на сервере.'
                try:
                    send_msg(client, response)
                except OSError:
                    pass
            return
        elif ACTION in message and message[ACTION] == EXIT and ACCOUNT_NAME in message \
                and self.names[message[ACCOUNT_NAME]] == client:
            self.remove_client(client)
        elif ACTION in message and message[ACTION] == GET_CONTACTS and USER in message \
                and self.names[message[USER]] == client:
            response = RESPONSE_202
            response[LIST_INFO] = self.database.get_contacts(message[USER])
            try:
                send_msg(client, response)
            except OSError:
                self.remove_client(client)
        elif ACTION in message and message[ACTION] == ADD_CONTACT and ACCOUNT_NAME in message and USER in message \
                and self.names[message[USER]] == client:
            self.database.add_contact(message[USER], message[ACCOUNT_NAME])
            try:
                send_msg(client, RESPONSE_200)
            except OSError:
                self.remove_client(client)
        elif ACTION in message and message[ACTION] == REMOVE_CONTACT and ACCOUNT_NAME in message and USER in message \
                and self.names[message[USER]] == client:
            self.database.remove_contact(message[USER], message[ACCOUNT_NAME])
            try:
                send_msg(client, RESPONSE_200)
            except OSError:
                self.remove_client(client)
        elif ACTION in message and message[ACTION] == USERS_REQUEST and ACCOUNT_NAME in message \
                and self.names[message[ACCOUNT_NAME]] == client:
            response = RESPONSE_202
            response[LIST_INFO] = [user[0]
                                   for user in self.database.users_list()]
            try:
                send_msg(client, response)
            except OSError:
                self.remove_client(client)
        elif ACTION in message and message[ACTION] == PUBLIC_KEY_REQUEST and ACCOUNT_NAME in message:
            response = RESPONSE_511
            response[DATA] = self.database.get_pubkey(message[ACCOUNT_NAME])
            if response[DATA]:
                try:
                    send_msg(client, response)
                except OSError:
                    self.remove_client(client)
            else:
                response = RESPONSE_400
                response[ERROR] = 'Нет публичного ключа для данного пользователя'
                try:
                    send_msg(client, response)
                except OSError:
                    self.remove_client(client)
        else:
            response = RESPONSE_400
            response[ERROR] = 'Некорректный запрос'
            try:
                send_msg(client, response)
            except OSError:
                self.remove_client(client)

    def autorize_user(self, message, sock):
        '''Метод реализующий авторизцию пользователей.'''
        logger.debug(f'Старт процесс авторизации пользователя {message[USER]}')
        if message[USER][ACCOUNT_NAME] in self.names.keys():
            response = RESPONSE_400
            response[ERROR] = 'Имя пользователя уже занято'
            try:
                logger.debug(f'Имя пользователя занято, отправлен {response}')
                send_msg(sock, response)
            except OSError:
                logger.debug('OS Error')
                pass
            self.clients.remove(sock)
            sock.close()
        elif not self.database.check_user(message[USER][ACCOUNT_NAME]):
            response = RESPONSE_400
            response[ERROR] = 'Пользователь не зарегистрирован.'
            try:
                logger.debug(f'Пользователь не найден, отправлен {response}')
                send_msg(sock, response)
            except OSError:
                pass
            self.clients.remove(sock)
            sock.close()
        else:
            logger.debug('Пользователь валиден, проверка пароля.')
            message_auth = RESPONSE_511
            random_str = binascii.hexlify(os.urandom(64))
            message_auth[DATA] = random_str.decode('ascii')
            hash = hmac.new(
                self.database.get_hash(
                    message[USER][ACCOUNT_NAME]),
                random_str,
                'MD5')
            digest = hash.digest()
            logger.debug(f'Auth message = {message_auth}')
            try:
                send_msg(sock, message_auth)
                ans = get_msg(sock)
            except OSError as err:
                logger.debug('Error in auth, data:', exc_info=err)
                sock.close()
                return
            client_digest = binascii.a2b_base64(ans[DATA])
            if RESPONSE in ans and ans[RESPONSE] == 511 and hmac.compare_digest(
                    digest, client_digest):
                self.names[message[USER][ACCOUNT_NAME]] = sock
                client_ip, client_port = sock.getpeername()
                try:
                    send_msg(sock, RESPONSE_200)
                except OSError:
                    self.remove_client(message[USER][ACCOUNT_NAME])
                self.database.user_login(
                    message[USER][ACCOUNT_NAME],
                    client_ip,
                    client_port,
                    message[USER][PUBLIC_KEY])
            else:
                response = RESPONSE_400
                response[ERROR] = 'Неверный пароль.'
                try:
                    send_msg(sock, response)
                except OSError:
                    pass
                self.clients.remove(sock)
                sock.close()

    def service_update_lists(self):
        '''Метод реализующий отправки сервисного сообщения 205 клиентам.'''
        for client in self.names:
            try:
                send_msg(self.names[client], RESPONSE_205)
            except OSError:
                self.remove_client(self.names[client])