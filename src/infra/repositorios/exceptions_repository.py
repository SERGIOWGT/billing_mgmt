#
# CLASSE DESENVOLVIDA EM COMO REPOSITORIO (REPOSITORY PATTERN) DOS OBJETOS DE EXCEÇOES DO ROBOT QUE ESTAO NA PLANIHLA DE ALOJAMENTOS
#


from dataclasses import dataclass
from typing import Any
import io
import pandas as pd
from src.infra.handlers.exception_handler import ApplicationException


@dataclass
class ExceptionRepository:
    _exceptions = {}

    def from_excel(self, stream_file: Any) -> None:
        df_ = pd.read_excel(io.BytesIO(stream_file), sheet_name="#EXCEÇOES")
        df = df_.where(pd.notnull(df_), None)

        cols = df.shape[1]
        expected_columns = ['#ORIGEM', '#FORNECEDOR', '#ID_EXEPÇÃO', '#AFETAÇÃO', '#VALOR']
        ApplicationException.when(cols != len(expected_columns), 'A Sheet "#EXCEÇOES" da planilha de Alojamentos deve ter 4 colunas. ')
        actual_columns = df.columns.tolist()
        ApplicationException.when(expected_columns != actual_columns, f'A sheet "#EXCEÇOES" da planilha de Alojamentos deveria ter as seguintes colunas {expected_columns}.')

        for _, row in df.iterrows():
            accommodation_name_in = row[expected_columns[0]]
            except_type = row[expected_columns[2]]
            nome_concessionaria = row[expected_columns[1]]
            accommodations_name_out = row[expected_columns[3]]
            if except_type == 2:
                valor = row[expected_columns[4]]
                self._exceptions[(accommodation_name_in, nome_concessionaria)] = (except_type, valor)
            else:
                vet_accommodations = accommodations_name_out.split(';')
                ApplicationException.when(len(vet_accommodations) == 0, f'O alojamento "{accommodation_name_in}" esta com registro de exceção incompativel. [{accommodations_name_out}]')
                self._exceptions[(accommodation_name_in, nome_concessionaria)] = (except_type, vet_accommodations)

    def get(self, accomm_id: str, service_provider_name: str)  -> Any:
        x = self._exceptions.get((accomm_id, service_provider_name), None)
        return x