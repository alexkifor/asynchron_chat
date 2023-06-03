import sys
import os
import logging
sys.path.append('../')
from variables import LOG_LEVEL


LOG =  logging.getLogger('client')
PATH = os.path.dirname(os.path.abspath(__file__))
PATH = os.path.join(PATH, 'logs/client/client.log')
LOG_FILE = logging.FileHandler(PATH, encoding='utf-8')
SERV_FORMAT = logging.Formatter('%(asctime)s %(levelname)-10s %(message)s')
LOG_FILE.setFormatter(SERV_FORMAT)
LOG.addHandler(LOG_FILE)
LOG.setLevel(LOG_LEVEL)


