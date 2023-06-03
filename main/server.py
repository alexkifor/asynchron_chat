from socket import *
import sys
import json
from main.utils import send_msg, get_msg
from main.variables import *



def handler_client_msg(data):
    '''
    Функция обрабатывает сообщения от клиента и выдает ответ в виде словаря
    :param data:
    :return:
    '''
    if 'action' in data and data['action'] == 'presence' and 'type' in data and data['type'] == 'status' and 'time' in data \
          and 'user' in data and data['user']['account_name'] == 'Guest':
        return {
            'response': 200
        }
    else:
        return {
            'response': 400,
            'error': 'Bad request'
        }


def main():
    '''
    Функция загружает параметры из командной строки, 
    если параметров нет задает параметры по умолчанию . Создает сокет
    и прослушивает указанный адрес.
    '''
    try:
        if '-p' in sys.argv:
            port = int(sys.argv[sys.argv.index('-p') + 1])
            if port < 1024 or port > 65535:
                raise ValueError
        else:
            port = DEFAULT_PORT
    except IndexError:
         print('После параметра -p нужно указать номер порта')
         sys.exit(1)
    except ValueError:
         print("Значение порта должно быть целым числом от 1024 до 65535")
         sys.exit(1)

    try:
        if '-a' in sys.argv:
            ip = sys.argv[sys.argv.index('-a') + 1]
        else:
            ip = ''
    except IndexError:
        print('После параметра -a укажите адрес который будет слушать сервер')
        sys.exit(1)

    s = socket(AF_INET, SOCK_STREAM)   # Создает сокет TCP
    s.bind((ip, port))                 # Присваивает порт 8888
    s.listen(5)                        # Переходит в режим ожидания запросов;

    while True:
        client, addr = s.accept()
        try:
            msg_from_client = get_msg(client)
            print(msg_from_client)
            resp = handler_client_msg(msg_from_client)
            send_msg(client, resp)
            client.close()
        except (ValueError, json.JSONDecodeError):
                print('Принято некорретное сообщение от клиента.')
                client.close()




if __name__ == '__main__':
     main()