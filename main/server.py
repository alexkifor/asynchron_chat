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
def handler_client_msg(data, msg_list, client, clients, names):
    '''
    Функция обрабатывает сообщения от клиента и выдает ответ в виде словаря
    :param data:
    :return:
    '''
    SERV_LOG.debug(f'parsig message from client {data}')
    if 'action' in data and data['action'] == 'presence' and 'time' in data \
        and 'user' in data:
            if data['user']['account_name'] not in names.keys():
                names[data['user']['account_name']] = client
                send_msg(client, {'response': 200})
            else:
                send_msg(client, {
                    'response': 400,
                    'error': 'Name already in use'
                    })
                clients.remove(client)
                client.close()
            return
    elif 'action' in data and data['action'] == 'message' and 'to' in data and 'time' in data \
        and 'from' in data and 'msg_text' in data:
        msg_list.append(data)
        return
    elif 'action' in data and data['action'] == 'exit' and 'account_name' in data:
        clients.remove(names[data['account_name']])
        names[data['account_name']].close()
        del names[data['account_name']]
        return
    else:
        send_msg(client, {
            'response': 400,
            'error': 'Incorrect response'
        })
        return 
    
def proc_msg_to_client(msg, names, cli_sock):
    if msg['to'] in names and names[msg['to']] in cli_sock:
        send_msg(names[msg['to']], msg)
        SERV_LOG.info(f"message sent to user {msg['to']} from user {msg['from']}")
    elif msg['to'] in names and names[msg['from']] not in cli_sock:
        raise ConnectionError
    else:
        SERV_LOG.error(f"user {msg['to']} not register on the server, sending message is not imposible")


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
    names = {}
    
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
                    handler_client_msg(get_msg(client), messages, client, clients, names)
                except:
                    SERV_LOG.info(f"client {client.getpeername()} disconnected from the server")
                    clients.remove(client)
        for msg in messages:
            try:
                proc_msg_to_client(msg, names, send_cli_lst)
            except:
                SERV_LOG.info(f"Connection with user {msg['to']} was lost")
                clients.remove(names[msg['to']])
                del names[msg['to']]
        messages.clear()
      




if __name__ == '__main__':
     main()