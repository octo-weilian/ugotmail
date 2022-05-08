from .logginghandler import LOGGER
import configparser
import time
import os
import logging
from dotenv import load_dotenv
import schedule
import json

#load configfiles
CACHE_CONFIG = configparser.ConfigParser()
CACHE_INI = "logs/cacheUID.ini"
CACHE_CONFIG.read(CACHE_INI)

IMAP_INI = "imapConfig.ini"
IMAP_CONFIG = configparser.ConfigParser()
IMAP_CONFIG.read(IMAP_INI)

load_dotenv()