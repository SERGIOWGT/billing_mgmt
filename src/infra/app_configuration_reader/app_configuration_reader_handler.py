import json
import os
from dataclasses import dataclass
from .iapp_configuration_reader import IAppConfigurationReaderHandler
from ..exception_handler import ApplicationException

@dataclass
class AppConfigurationReaderHandler (IAppConfigurationReaderHandler):
    _dict_config = {}

    def __init__(self, file_name: str):
        _complete_file_name = os.path.join(os.path.abspath(os.curdir), file_name)
        ApplicationException.when(not os.path.exists(_complete_file_name), f'Arquivo de configuração não encontrado. {file_name}')

        with open(_complete_file_name, 'r') as file:
            self._dict_config = json.load(file)

    def get(self, key_name: str):
        _dict = self._dict_config
        for key in key_name.split('.'):
            try:
                _dict = _dict[key]
            except KeyError:
                return ''
        return _dict
