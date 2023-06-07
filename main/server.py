from socket import *
import sys
import json
sys.path.append('../')
from main.utils import send_msg, get_msg
from main.variables import *
import logging
import log.config_server
from decos import log


SERV_LOG = logging.getLogger('server')

@log
def handler_client_msg(data:dict):
    '''
    Функция обрабатывает сообщения от клиента и выдает ответ в виде словаря
    :param data:
    :return:
    '''
    SERV_LOG.debug(f'parsig message from client {data}')
    if 'action' in data and data['action'] == 'presence' and 'type' in data and data['type'] == 'status' and 'time' in data \
        and 'user' in data and data['user']['account_name'] == 'Guest':
        SERV_LOG.info('OK, message contains without error')
        return {'response': 200}
    else:
        SERV_LOG.error('WRONG, massege contains error')
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
    SERV_LOG.info(f"trying to start socket from on the server")
    try:
        if '-p' in sys.argv:
            port = int(sys.argv[sys.argv.index('-p') + 1])
            if port < 1024 or port > 65535:
                SERV_LOG.critical(f"starting server on an invalid {port} port")
                sys.exit(1)                  
        else:
            port = DEFAULT_PORT
         
    except IndexError:
         SERV_LOG.critical(f"after '-p' port value not set")
         sys.exit(1)
    except ValueError:
         SERV_LOG.critical("after '-p' wrong port value set")
         sys.exit(1)

    try:
        if '-a' in sys.argv:
            ip = sys.argv[sys.argv.index('-a') + 1]
            SERV_LOG.info(f'server socket waiting for connection on {port} port with ip address: {ip}')
        else:
            ip = ''
            SERV_LOG.info(f'server socket waiting for connection on {port} from any ip address')
    except IndexError:
        SERV_LOG.critical(f"after '-a' ip address value not set")
        sys.exit(1)
    
    
    s = socket(AF_INET, SOCK_STREAM)   # Создает сокет TCP
    s.bind((ip, port))                 # Присваивает порт 8888
    s.listen(5)                        # Переходит в режим ожидания запросов;

    while True:
        client, addr = s.accept()
        SERV_LOG.info(f'connection with {addr}')
        try:
            msg_from_client = get_msg(client)
            SERV_LOG.debug(f'message received {msg_from_client}')
            resp = handler_client_msg(msg_from_client)
            SERV_LOG.info(f'generating response {resp}')
            send_msg(client, resp)
            SERV_LOG.info(f'sending response {resp} to client')
            SERV_LOG.debug(f'disable connection with {addr}')
            client.close()
        except (ValueError, json.JSONDecodeError):
                SERV_LOG.error(f'WRONG, incoorect data received from client {addr}, connection is closed ')
                client.close()




if __name__ == '__main__':
     main()