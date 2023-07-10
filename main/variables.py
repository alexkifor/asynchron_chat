import logging


DEFAULT_PORT = 7777
DEFAULT_IP = '127.0.0.1'
LOG_LEVEL = logging.DEBUG

SERVER_DB = 'sqlite:///server_db.db3'
ACTION = 'action'
TIME = 'time'
USER = 'user'
ACCOUNT_NAME = 'account_name'
SENDER = 'from'
DESTINATION = 'to'
PRESENCE = 'presence'
RESPONSE = 'response'
ERROR = 'error'
MESSAGE = 'message'
MESSAGE_TEXT = 'mess_text'
EXIT = 'exit'
GET_CONTACTS = 'get_contacts'
LIST_INFO = 'data_list'
REMOVE_CONTACT = 'remove'
ADD_CONTACT = 'add'
USERS_REQUEST = 'get_users'

RESPONSE_200 = {RESPONSE: 200}
RESPONSE_202 = {RESPONSE: 202,
                LIST_INFO: None
                }
RESPONSE_400 = {
            RESPONSE: 400,
            ERROR: None
        }