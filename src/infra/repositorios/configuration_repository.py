
from dataclasses import dataclass
import io
import os

import pandas as pd
from pyparsing import Any

@dataclass
class ConfigurationRepository:
    _configurations: dict

    def __init__(self):
        self._configurations = {}

    def get_key(self, key: str) -> str:
        return self._configurations.get(key, '')

    def from_excel(self, stream_file: Any) -> None:
        df_ = pd.read_excel(io.BytesIO(stream_file), sheet_name="#CONFIG")
        df = df_.where(pd.notnull(df_), None)

        for row in range(df.shape[0]):
            if df.iat[row, 1] is None:
                break

            self._configurations[df.iat[row, 0]] = df.iat[row, 1]
