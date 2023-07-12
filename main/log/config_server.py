import sys
import os
from logging.handlers import TimedRotatingFileHandler
sys.path.append('../')
from main.variables import *


LOG = logging.getLogger('server')
PATH = os.path.dirname(os.path.abspath(__file__))
PATH = os.path.join(PATH, 'logs/server/server.log')
LOG_FILE = TimedRotatingFileHandler(PATH, encoding='utf-8', interval=1, when='H')
SERV_FORMAT = logging.Formatter('%(asctime)s %(levelname)-10s %(message)s')
LOG_FILE.setFormatter(SERV_FORMAT)
LOG.addHandler(LOG_FILE)
LOG.setLevel(LOG_LEVEL)


