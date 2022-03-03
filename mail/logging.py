import logging
from logging.handlers import RotatingFileHandler

def init_logger():
    LOGGER = logging.getLogger("idle_logger")
    LOGGER.setLevel(logging.DEBUG)
    handler = RotatingFileHandler("mail/logfile.log",mode='a+',maxBytes=2e6,backupCount=1)
    formatter = logging.Formatter('%(asctime)s - %(message)s',datefmt='%Y-%m-%d %H:%M:%S')
    handler.setFormatter(formatter)
    LOGGER.addHandler(handler)
    return LOGGER