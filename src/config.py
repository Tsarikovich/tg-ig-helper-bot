import logging.config
import os

from notifiers.logging import NotificationHandler
from selenium import webdriver


ID_TELEGRAM_CHAT = 1736337003

PROXY = {
    'http': '',
    'https': '',
}

SELENIUMWIRE_OPTIONS = {'proxy': PROXY}


class PathTo:
    DOWNLOAD = 'photos/'
    SOURCE_TRAFFIC_PEOPLE = 'source_traffic_accounts/people.txt'
    SOURCE_TRAFFIC_GROUPS = 'source_traffic_accounts/groups.txt'
    USED_USERS = 'used_users.txt'


class HashtagsGen:
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('--ignore-certificate-errors')
    chrome_options.add_argument('--disable-extensions')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument(
        '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
        'AppleWebKit/537.36 (KHTML, like Gecko) '
        'Chrome/94.0.4606.81 Safari/537.36'
    )
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')

    URL = 'https://displaypurposes.com/'


LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'default_formatter': {
            'format': '[%(levelname)s:%(asctime)s] %(message)s'
        },
    },
    'handlers': {
        'stream_handler': {
            'class': 'logging.StreamHandler',
            'formatter': 'default_formatter',
        },
    },
    'loggers': {
        'my_logger': {
            'handlers': ['stream_handler'],
            'level': 'DEBUG',
            'propagate': True,
        }
    },
}

logging.config.dictConfig(LOGGING_CONFIG)

params = {'token': os.environ['TOKEN'], 'chat_id': ID_TELEGRAM_CHAT}

tg_handler = NotificationHandler('telegram', defaults=params)
logger = logging.getLogger('my_logger')
tg_handler.setLevel(logging.INFO)
logger.addHandler(tg_handler)

with open('../useragents.txt') as file:
    USERAGENTS = [acc.split(':')[4] for acc in file.read().split('\n')]

with open(PathTo.SOURCE_TRAFFIC_GROUPS) as file:
    ids_strings = file.read().split('\n')
    ids = [item.split(',') for item in ids_strings]
