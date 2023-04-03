import json
import os
from dataclasses import dataclass
from src.infra.exception_handler import ApplicationException
from src.infra.app_configuration_reader.iapp_configuration_reader import IAppConfigurationReader

@dataclass
class AppConfigurationReader (IAppConfigurationReader):
    _dict_config = {}

    def __init__(self, file_name: str):
        ApplicationException.when(not os.path.exists(file_name), f'Arquivo de configuração não encontrado. {file_name}')

        with open(file_name, 'r') as file:
            self._dict_config = json.load(file)

    def get(self, key_name: str)-> dict:
        _dict = self._dict_config
        for key in key_name.split('.'):
            try:
                _dict = _dict[key]
            except KeyError:
                return ''
        return _dict
