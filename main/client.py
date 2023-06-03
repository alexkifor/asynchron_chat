from socket import *
from variables import *
import sys
import json
import time
sys.path.append('../')
from main.utils import send_msg, get_msg
import logging
import log.config_client

CLI_LOG = logging.getLogger('client')

def create_msg(account_name="Guest"):
    '''
    Функция формирует сообщение для сервера
    :param account_name:
    :return:
    '''
    msg = {
        "action": "presence",
        "time": time.time(),
        "type": "status",
        "user": {
            "account_name": account_name,
        } 
    }

    CLI_LOG.debug(f"generated message {msg} to send the server from {account_name}")
    return msg


def handler_server_msg(data):
    '''
    Функция обрабатывает сообщения от сервера и выдает ответ в виде строки
    :param data:
    :return:
    '''
    CLI_LOG.debug(f'parsing response from the server {data}')
    if 'response' in data:    
        if data['response'] == 200:
            CLI_LOG.info(f'successful, client received a response from sever  : 200: OK')
            return '200: OK'
        CLI_LOG.info(f'successful, client received a response from sever: 400: {data["error"]} ')
        return f'400: {data["error"]}'
    raise ValueError



def main():
    '''
    Функция загружает параметры из командной строки адрес и порт. Создает соединение с сервером
    Отправляет сообщение на сервер и принимает ответ от сервера.
    '''
    CLI_LOG.info(f'trying to start socket on the client')
    try:
        server_port = int(sys.argv[2])
        server_ip = sys.argv[4]
        if server_port < 1024 or server_port > 65535:
            raise ValueError
    except IndexError:
        server_ip = DEFAULT_IP
        server_port = DEFAULT_PORT
    except ValueError:
        CLI_LOG.critical(f"starting client on an invalid {server_port} port")
        sys.exit(1)

    s = socket(AF_INET, SOCK_STREAM) # Создать сокет TCP
    CLI_LOG.info(f'started client socket on {server_port} port with ip_address {server_ip}')
    s.connect((server_ip, server_port)) # Соединиться с сервером
    CLI_LOG.info(f'server connection established')
    presence_msg = create_msg()
    send_msg(s, presence_msg)
    CLI_LOG.info(f'sending message {presence_msg} from client to server')
    try:
        answer = handler_server_msg(get_msg(s))
        print(answer)
    except (ValueError, json.JSONDecodeError):  
        CLI_LOG.error(f'invalid message received from client')
        

if __name__ == '__main__':
     main()