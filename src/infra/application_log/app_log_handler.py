from dataclasses import dataclass
from logging import Logger
from typing import Any, List
import requests
#TOKEN_INFO = '6292020167:AAF9X9jUsThCvDBS_x5sNWu24zY6xq2Vioc'
#TOKEN_ERROR = TOKEN_INFO
#TOKEN_WARN = '6292814452:AAFvUzSUQSwBsGUCoJxAB16_UvxOg_-oUZk'


@dataclass
class ApplicationLogHandler():
    _log: Logger = Any
    _bot = Any
    token_execution = ''
    token_error = ''
    token_warn = ''
    list_execution_chat_id = ''
    list_warn_chat_id = ''
    
    def _send_telegram(self, apiToken, list, msg):
        #chatID = '1562103759'
        #chatID = '914915746'
        apiURL = f'https://api.telegram.org/bot{apiToken}/sendMessage'

        try:
            for _, chat_id in enumerate(list):
                _ = requests.post(apiURL, json={'chat_id': chat_id, 'text': msg}, timeout=10000)
        except Exception:
            ...

    def __init__(self, log):
        self._log = log

    def info(self, msg, instant_msg: bool = False, warn=False):
        self._log.info(msg)
        
        if self.token_execution:
            if instant_msg:
                self._send_telegram(self.token_execution,  self.list_execution_chat_id, msg)
            if warn:
                self._send_telegram(self.token_warn, self.list_warn_chat_id , msg)


    def error(self, msg, instant_msg: bool = True):
        self._log.error(msg)
        if self.token_execution and instant_msg:
                self._send_telegram(self.token_error, self.list_execution_chat_id, msg)

    def warning(self, msg, instant_msg: bool = True):
        self._log.error(msg)
        if self.token_execution and instant_msg:
                self._send_telegram(self.token_warn, self.list_warn_chat_id, msg)
