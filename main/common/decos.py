import sys
import logging
import inspect
import socket


def log(func_to_log):
    '''
    Декоратор, выполняющий логирование вызовов функций.
    Сохраняет события типа debug, содержащие
    информацию о имени вызываемой функиции, параметры с которыми
    вызывается функция, и модуль, вызывающий функцию.
    '''
    def wrapper(*args, **kwargs):
        func_out = func_to_log(*args, **kwargs)
        data = sys.argv[0].split('.')[0]
        LOG = logging.getLogger(f'{data}')
        LOG.debug(
            f'A function {func_to_log.__name__} was called with parameters {args}, {kwargs} from the function {inspect.stack()[1][3]}')
        return func_out

    return wrapper


def login_required(func):
    '''
    Декоратор, проверяющий, что клиент авторизован на сервере.
    Проверяет, что передаваемый объект сокета находится в
    списке авторизованных клиентов.
    За исключением передачи словаря-запроса
    на авторизацию. Если клиент не авторизован,
    генерирует исключение TypeError
    '''
    def checker(*args, **kwargs):
        from main.server.core import Server
        from main.common.variables import ACTION, PRESENCE
        if isinstance(args[0], Server):
            found = False
            for arg in args:
                if isinstance(arg, socket.socket):
                    for client in args[0].names:
                        if args[0].names[client] == arg:
                            found = True
            for arg in args:
                if isinstance(arg, dict):
                    if ACTION in arg and arg[ACTION] == PRESENCE:
                        found = True
            if not found:
                raise TypeError
        return func(*args, **kwargs)

    return checker
