from socket import *
from main.variables import *
import sys
import json
import time
from main.utils import send_msg, get_msg


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

    return msg


def handler_server_msg(data):
    '''
    Функция обрабатывает сообщения от сервера и выдает ответ в виде строки
    :param data:
    :return:
    '''
    if 'response' in data:
        if data['response'] == 200:
            return '200: OK'
        return f'400: {data["error"]}'
    raise ValueError



def main():
    '''
    Функция загружает параметры из командной строки адрес и порт. Создает соединение с сервером
    Отправляет сообщение на сервер и принимает ответ от сервера.
    '''
    try:
        server_port = int(sys.argv[2])
        server_ip = sys.argv[1]
        if server_port < 1024 or server_port > 65535:
            raise ValueError
    except IndexError:
        server_ip = DEFAULT_IP
        server_port = DEFAULT_PORT
    except ValueError:
        print('Значение порта должно быть целым числом от 1024 до 65535')
        sys.exit(1)

    s = socket(AF_INET, SOCK_STREAM) # Создать сокет TCP
    s.connect((server_ip, server_port)) # Соединиться с сервером
    presence_msg = create_msg()
    send_msg(s, presence_msg)
    try:
        answer = handler_server_msg(get_msg(s))
        print(answer)
    except (ValueError, json.JSONDecodeError):  
        print('Принято некорретное сообщение от клиента.')
        

if __name__ == '__main__':
     main()