from socket import *
import select
import sys
import time
sys.path.append('../')
from main.utils import send_msg, get_msg
from main.variables import *
import logging
import log.config_server
from decos import log


SERV_LOG = logging.getLogger('server')

@log
def handler_client_msg(data:dict, msg_list:list, cli_sock):
    '''
    Функция обрабатывает сообщения от клиента и выдает ответ в виде словаря
    :param data:
    :return:
    '''
    SERV_LOG.debug(f'parsig message from client {data}')
    if 'action' in data and data['action'] == 'presence' and 'time' in data \
        and 'user' in data and data['user']['account_name'] == 'Guest':
        send_msg(cli_sock, {'response': 200})
        return
    elif 'action' in data and data['action'] == 'message' and 'time' in data \
        and 'msg_text' in data:
        msg_list.append((data['account_name'], data['msg_text']))
        return
    else:
        send_msg(cli_sock, {
            'response': 400,
            'error': 'Bad request'
        })
        return 


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
    s.settimeout(1)
    s.listen(5)                        # Переходит в режим ожидания запросов;
    clients = []
    messages = []

    while True:
        try:
            client, addr = s.accept()   
        except OSError:
            pass
        else:
            SERV_LOG.info(f"connection server with {addr}")
            clients.append(client)
        
        rec_cli_lst = []
        send_cli_lst = []
        err_lst = []
        
        try:
            if clients:
                rec_cli_lst, send_cli_lst, err_lst = select.select(clients, clients, [], 0)
        except OSError:
            pass

        if rec_cli_lst:
            for client in rec_cli_lst:
                try:
                    handler_client_msg(get_msg(client), messages, client)
                except:
                    SERV_LOG.info(f"client {client.getpeername()} disconnected from the server")
                    clients.remove(client)
        if messages and send_cli_lst:
            msg = {
                'action':  'message',
                'sender' : messages[0][0],
                'time' : time.time(),
                'msg_text' : messages[0][1]
            }
            del messages[0]
            for client in send_cli_lst:
                try:
                    send_msg(client, msg)
                except:
                    SERV_LOG.info(f"client {client.getpeername()} disconnected from the server")
                    clients.remove(client)




if __name__ == '__main__':
     main()