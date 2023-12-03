#
# CLASSE DESENVOLVIDA EM COMO REPOSITORIO (REPOSITORY PATTERN) DOS OBJETOS DAS CONTAS COM ERROS
#

from dataclasses import dataclass
from datetime import datetime
import io
from typing import List
import pandas as pd
from pyparsing import Any
from src.infra.handlers.exception_handler import ApplicationException
from src.domain.entities.recorring_errors import RecorringError

@dataclass
class RecorringErrorsRepository:
    _recorring_error: List[RecorringError] = None

    def __init__(self):
        self._recorring_error = []

    def from_excel(self, stream_file: Any) -> None:
        df_ = pd.read_excel(io.BytesIO(stream_file), dtype={'NomeArquivo': object})
        df = df_.where(pd.notnull(df_), None)
        cols = df.shape[1]
        ApplicationException.when(cols != 2, 'Recorring Error Sheet must have 2 columns. ')
        expected_columns = ['Arquivo Original', 'Data Processamento']
        actual_columns = df.columns.tolist()

        ApplicationException.when(expected_columns != actual_columns, f'The Recorring Error Spreadsheet should have the columns {actual_columns}.')
        for _, row in df.iterrows():
            original_filename = row['Arquivo Original']
            obj_aux = row['Data Processamento']
            dt_processamento = obj_aux if isinstance(obj_aux, datetime) else datetime.strptime(obj_aux, "%d/%m/%Y %H:%M:%S")
            self._recorring_error.append(RecorringError(original_filename, dt_processamento))
            
        return

    def get_first(self, filename: str) -> RecorringError:
        for _file in self._recorring_error:
            if _file.file_name == filename:
                return _file
        return None

    def count(self) -> int:
        return len(self._recorring_error)
