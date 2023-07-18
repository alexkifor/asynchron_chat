Server module documentation
=================================================

Серверный модуль мессенджера. Обрабатывает словари - сообщения, хранит публичные ключи клиентов.

Использование

Модуль подерживает аргементы командной стороки:

1. -p - Порт на котором принимаются соединения
2. -a - Адрес с которого принимаются соединения.


Примеры использования:

``python server.py -p 8080``

*Запуск сервера на порту 8080*

``python server.py -a localhost``

*Запуск сервера принимающего только соединения с localhost*


server.py
~~~~~~~~~

Запускаемый модуль,содержит парсер аргументов командной строки и функционал инициализации приложения.

server. **arg_parser** ()
    Парсер аргументов командной строки, возвращает кортеж из 2 элементов:

	* адрес с которого принимать соединения
	* порт


server. **config_load** ()
    Функция загрузки параметров конфигурации из ini файла.
    В случае отсутствия файла задаются параметры по умолчанию.

core.py
~~~~~~~~~~~

.. autoclass:: server.core.Server
	:members:

server_db.py
~~~~~~~~~~~

.. autoclass:: server.server_db.ServerPool
	:members:

server_gui.py
~~~~~~~~~~~~~~

.. autoclass:: server.server_gui.StatWindow
	:members:

.. autoclass:: server.server_gui.RegisterUser
	:members:

.. autoclass:: server.server_gui.ConfigWindow
	:members:

.. autoclass:: server.server_gui.DelUserDialog
	:members:

.. autoclass:: server.server_gui.MainWindow
	:members:

