import logging
from logging.handlers import RotatingFileHandler

HANDLER = RotatingFileHandler("logs/logfile.log",maxBytes=2e6,backupCount=2)
HANDLER.setLevel(logging.DEBUG)

FORMATTER = logging.Formatter('%(asctime)s - %(message)s',datefmt='%Y-%m-%d %H:%M:%S')
HANDLER.setFormatter(FORMATTER)

LOGGER = logging.getLogger('logger')
LOGGER.setLevel(logging.INFO)
LOGGER.addHandler(HANDLER)




