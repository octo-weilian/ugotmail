from . import logginghandler
from . import parser

#client.py
import configparser
from contextlib import contextmanager
from imapclient import IMAPClient
import time
import schedule
import os
import logging
import keyring
import configparser

#parser.py
import email
from email.generator import BytesGenerator
import logging
import os

#initialize configfiles
CACHE_CONFIG = configparser.ConfigParser()
CACHE_INI = "logs/cacheUID.ini"
CACHE_CONFIG.read(CACHE_INI)

IMAP_INI = "imapConfig.ini"
IMAP_CONFIG = configparser.ConfigParser()
IMAP_CONFIG.read(IMAP_INI)

#logger
LOGGER = logging.getLogger('logger')