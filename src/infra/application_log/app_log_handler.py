from dataclasses import dataclass
from logging import Logger
from typing import Any
import requests


@dataclass
class ApplicationLogHandler():
    _log: Logger = Any
    _bot = Any
    
    def _send_telegram(self, msg):
        apiToken = '5806073657:AAGGz4AnYqATtzPeXTGY_KYQWTBaVhXdV74'
        chatID = '1562103759'
        apiURL = f'https://api.telegram.org/bot{apiToken}/sendMessage'

        try:
            response = requests.post(apiURL, json={'chat_id': chatID, 'text': msg})
        except Exception:
            ...

    def __init__(self, log):
        self._log = log

    def info(self, msg, instant_msg: bool = True):
        self._log.info(msg)
        if instant_msg:
            self._send_telegram(msg)
            
    def error(self, msg, instant_msg: bool = True):
        self._log.error(msg)
        if instant_msg:
            self._send_telegram(msg)
