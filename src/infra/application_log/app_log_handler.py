from dataclasses import dataclass
from logging import Logger
from typing import Any
import requests
TOKEN_INFO = '6292020167:AAF9X9jUsThCvDBS_x5sNWu24zY6xq2Vioc'
TOKEN_ERROR = TOKEN_INFO
TOKEN_WARN = '6292814452:AAFvUzSUQSwBsGUCoJxAB16_UvxOg_-oUZk'


@dataclass
class ApplicationLogHandler():
    _log: Logger = Any
    _bot = Any
    
    def _send_telegram(self, apiToken, msg):
        chatID = '1562103759'
        apiURL = f'https://api.telegram.org/bot{apiToken}/sendMessage'

        try:
            response = requests.post(apiURL, json={'chat_id': chatID, 'text': msg})
        except Exception:
            ...

    def __init__(self, log):
        self._log = log

    def info(self, msg, instant_msg: bool = False, warn=False):
        self._log.info(msg)
        if instant_msg:
            self._send_telegram(TOKEN_INFO, msg)
        if warn:
            self._send_telegram(TOKEN_WARN, msg)


    def error(self, msg, instant_msg: bool = True):
        self._log.error(msg)
        if instant_msg:
            self._send_telegram(TOKEN_ERROR, msg)

    def warning(self, msg, instant_msg: bool = True):
        self._log.error(msg)
        if instant_msg:
            self._send_telegram(TOKEN_WARN, msg)