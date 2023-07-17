import logging
import ipaddress
import sys

logger = logging.getLogger(sys.argv[0].split('.')[0])


class Port:
    '''
    Класс - дескриптор для номера порта.
    Позволяет использовать только порты с 1023 по 65536.
    При попытке установить неподходящий номер порта генерирует исключение.
    '''
    def __set__(self, instance, value):
        if value < 1024 or value > 65535:
            logger.critical(f"starting on an invalid {value} port")
            print(f"starting on an invalid {value} port")
            exit(1)
        instance.__dict__[self.name] = value

    def __set_name__(self, owner, name):
        self.name = name


class Addr:
    '''
       Класс - дескриптор для ip_адреса.
       Позволяет использовать только валидные ip_адреса.
       При попытке установить неподходящий ip_адрес генерирует исключение.
       '''
    def __set__(self, instance, value):

        if value == '':
            instance.__dict__[self.name] = value
        else:
            try:
                ipaddress.ip_address(value)

            except:
                logger.critical(f"starting on an invalid {value} host")
                print(f"starting on an invalid {value} host")
                exit(1)
            else:
                instance.__dict__[self.name] = value

    def __set_name__(self, owner, name):
        self.name = name
