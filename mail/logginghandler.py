import logging
from logging.handlers import RotatingFileHandler

def init_logger():
    LOGGER = logging.getLogger("logger")
    LOGGER.setLevel(logging.DEBUG)
    handler = RotatingFileHandler("logs/logfile.log",mode='a+',maxBytes=2e6,backupCount=2)
    formatter = logging.Formatter('%(asctime)s - %(message)s',datefmt='%Y-%m-%d %H:%M:%S')
    handler.setFormatter(formatter)
    LOGGER.addHandler(handler)
    return LOGGER