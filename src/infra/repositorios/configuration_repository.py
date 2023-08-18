#
# CLASSE DESENVOLVIDA EM COMO REPOSITORIO (REPOSITORY PATTERN) DOS OBJETOS DE CONFIGURACAO DO ROBOT QUE ESTAO NA PLANIHLA DE ALOJAMENTOS
#

from dataclasses import dataclass
import io
import pandas as pd
from pyparsing import Any

@dataclass
class ConfigurationRepository:
    _configurations: dict

    def __init__(self):
        self._configurations = {}

    def number_of_configs(self) -> int:
        return len(self._configurations)


    def get_key(self, key: str) -> str:
        return self._configurations.get(key, '')

    def from_excel(self, stream_file: Any) -> None:
        df_ = pd.read_excel(io.BytesIO(stream_file), sheet_name="#CONFIG")
        df = df_.where(pd.notnull(df_), None)

        for row in range(df.shape[0]):
            if df.iat[row, 1] is None:
                break

            self._configurations[df.iat[row, 0]] = df.iat[row, 1]
