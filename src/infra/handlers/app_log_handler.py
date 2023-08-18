#
# CLASSE ESPECÍFICA PARA EXECUTAR OS LOGS DA APLICAÇÃO
# 

from dataclasses import dataclass
from logging import Logger
from typing import Any
from datetime import datetime
import requests

@dataclass
class ApplicationLogHandler():
    _log: Logger = Any
    _bot = Any
    _str_data_execucao: str = ''
    token_execution = ''
    token_error = ''
    token_warn = ''
    list_execution_chat_id = ''
    list_warn_chat_id = ''


    def _send_message(self, tipo, msg):
        ...
        #str_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        #apiURL = 'https://hook.us1.make.com/es853u8com87xk8fni56fdnm8tshg8vk'

        #try:
        #    _ = requests.post(apiURL, json={'execucao': self._str_data_execucao, 'horario': str_now, 'tipo': tipo, 'mensagem': msg}, timeout=10000)
        #except Exception:
        #    ...
    
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
        self._str_data_execucao = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def save_message(self, msg: str, execution: bool = False, error: bool = False):
        self._log.info(msg)
        if error:
            self._send_message('Error', msg)
        elif execution:
            self._send_message('Execution', msg)
        else:
            self._send_message('Info', msg)

    def save_message_qd30(self, tipo_alerta, num_processados, num_erros, num_sem_alojamentos, link_qd28, link_exports):
        str_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        apiURL = 'https://hook.us1.make.com/gq4047iq6xvncq1mm630dy24ivbr21c7'

        jsonData = {
            "DATA_ALERTA": str_now,
            "TIPO_ALERTA": tipo_alerta,
            "QT_FICHEIROS_PROCESSADOS": num_processados,
            "QT_FICHEIROS_ERRO": num_erros,
            "QT_ficheiros sem alojamento": num_sem_alojamentos,
            "LINK_QD28": link_qd28,
            "LINK_EXEC": link_exports
        }

        try:
            _ = requests.post(apiURL, json=jsonData, timeout=10000)
        except Exception:
            ...
            
    def save_message_email(self, list):
        apiURL = 'https://hook.us1.make.com/vkk4ty80fpr92s11kw5xw14kh1gp51td'


        try:
            _ = requests.post(apiURL, json=list, timeout=10000)
        except Exception:
            ...
