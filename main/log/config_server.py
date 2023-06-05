import sys
import os
import logging
from logging.handlers import TimedRotatingFileHandler
sys.path.append('../')
from variables import LOG_LEVEL


LOG =  logging.getLogger('server')
PATH = os.path.dirname(os.path.abspath(__file__))
PATH = os.path.join(PATH, 'logs/server/server.log')
LOG_FILE = TimedRotatingFileHandler(PATH, encoding='utf-8', interval=5, when='M')
SERV_FORMAT = logging.Formatter('%(asctime)s %(levelname)-10s %(message)s')
LOG_FILE.setFormatter(SERV_FORMAT)
LOG.addHandler(LOG_FILE)
LOG.setLevel(LOG_LEVEL)


