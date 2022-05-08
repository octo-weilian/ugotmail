import logging
from logging.handlers import RotatingFileHandler

LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)

HANDLER = RotatingFileHandler("logs/logfile.log",maxBytes=2e6,backupCount=2)
HANDLER.setLevel(logging.INFO)
FORMATTER = logging.Formatter('%(asctime)s - %(message)s',datefmt='%Y-%m-%d %H:%M:%S')
HANDLER.setFormatter(FORMATTER)

LOGGER.addHandler(HANDLER)




