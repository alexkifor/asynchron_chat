from socket import *
import sys
import json
from utils import send_msg
from variables import *



def handler_client_msg(data:bytes):
    '''
    Функция обрабатывает сообщения от клиента и выдает ответ в виде словаря
    :param data:
    :return:
    '''
    input = json.loads(data.decode('utf-8'))
    if input["action"] and input["time"] and input["user"] \
          and input["user"]['account_name']:
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
    except ValueError:
         print("Значение порта должно быть целым числом от 1024 до 65535")

    try:
        if '-a' in sys.argv:
            ip = sys.argv[sys.argv.index('-a') + 1]
        else:
            ip = DEFAULT_IP
    except IndexError:
        print('После параметра -a укажите адрес который будет слушать сервер')

    s = socket(AF_INET, SOCK_STREAM)   # Создает сокет TCP
    s.bind((ip, port))                 # Присваивает порт 8888
    s.listen(5)                        # Переходит в режим ожидания запросов;

    while True:
        client, addr = s.accept()
        try:
            data = client.recv(640)
            print('Сообщение: ', data.decode('utf-8'), ', было отправлено клиентом: ',
            addr)
            msg = json.dumps(handler_client_msg(data)) 
            send_msg(client, msg)
            client.close()
        except (ValueError, json.JSONDecodeError):
                print('Принято некорретное сообщение от клиента.')
                client.close()




if __name__ == '__main__':
     main()