import json

from main.common.decos import log

@log
def get_msg(client):
    '''
    Функция приёма сообщений от удалённых компьютеров.
    Принимает сообщения JSON, декодирует полученное сообщение
    и проверяет что получен словарь.
    :param client: сокет для передачи данных.
    :return: словарь - сообщение.
    '''
    encode_resp = client.recv(1024)
    if isinstance(encode_resp, bytes):
        json_resp = encode_resp.decode('utf-8')
        resp = json.loads(json_resp)
        if isinstance(resp, dict):
            return resp
        raise ValueError
    raise ValueError

@log
def send_msg(socket, msg):
    '''
    Функция отправки словарей через сокет.
    Кодирует словарь в формат JSON и отправляет через сокет.
    :param sock: сокет для передачи
    :param message: словарь для передачи
    :return: ничего не возвращает
    '''
    json_msg = json.dumps(msg)
    msg_bytes = json_msg.encode('utf-8')
    socket.send(msg_bytes)

