from .logginghandler import LOGGER
import configparser
import time
import os
import sys
import logging
from dotenv import load_dotenv,find_dotenv
import schedule
import json

#load existing cached UID
CACHE_CONFIG = configparser.ConfigParser()
CACHE_INI = "logs/cacheUID.ini"
CACHE_CONFIG.read(CACHE_INI)

#load app configfile
APP_INI = "appConfig.ini"
APP_CONFIG = configparser.ConfigParser()
APP_CONFIG.read(APP_INI)

secrets = APP_CONFIG["secrets"]["dotenv"]
if find_dotenv(secrets):
    load_dotenv(secrets)
else:
    LOGGER.error(f"FileNotFoundError: {secrets}. Program exited.")
    sys.exit()
