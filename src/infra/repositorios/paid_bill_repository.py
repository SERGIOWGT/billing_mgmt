from dataclasses import dataclass
import io
import os
from typing import List
import pandas as pd
from pyparsing import Any
from src.domain.entities.paid_utility_bill import PaidUtilityBill
from src.domain.enums.service_provider_enum import ServiceProviderEnum
from src.domain.enums.service_type_enum import ServiceTypeEnum

from src.infra.exception_handler import ApplicationException

@dataclass
class PaidBillRepository:
    _paid_bills: List[PaidUtilityBill] = None

    def __init__(self):
        self._paid_bills = []

    def from_excel(self, file_path: Any) -> None:
        if not os.path.exists(file_path):
            return

        df_ = pd.read_excel(file_path, dtype={'N. Documento / N. Fatura': object})
        df = df_.where(pd.notnull(df_), None)
        cols = df.shape[1]
        ApplicationException.when(cols != 22, 'History Sheet must have 22 columns. ')
        expected_columns = ['QQ Destino', 'Alojamento', 'Ano Emissao', 'Mes Emissao', 'Concessionaria', 'Tipo Servico',
                            'Tipo Documento', 'N. Contrato', 'N. Cliente', 'N. Contribuinte', 'Local / Instalacao',
                            'N. Documento / N. Fatura', 'Periodo Referencia', 'Inicio Referencia', 'Fim Referencia',
                            'Emissao', 'Vencimento', 'Valor', 'Arquivo Google', 'Arquivo Original', 'Data Processamento']
        actual_columns = df.columns.tolist()

        ApplicationException.when(expected_columns != actual_columns, f'The Historical Spreadsheet should have the columns {actual_columns}.')
        for _, row in df.iterrows():
            provider_service_name = row['Concessionaria']
            provider_service_name = provider_service_name.replace('\n', '')
            service_type_name = row['Tipo Servico']
            service_type_name = service_type_name.replace('\n', '')
            accommodation_name = row['Alojamento']
            id_documento = row['N. Documento / N. Fatura']
            dt_emissao = row['Emissao']
            original_file_id = row['Arquivo Google']

            self._paid_bills.append(PaidUtilityBill(provider_service_name, service_type_name, accommodation_name, id_documento, dt_emissao, original_file_id))

    def get(self, concessionaria: ServiceProviderEnum, tipo_servico: ServiceTypeEnum, nome_Accommodation: str, id_documento: str) -> bool:
        def achou(conta):
            return conta.nome_Accommodation == nome_Accommodation and conta.id_documento == id_documento and conta.nome_concessionaria == ServiceProviderEnum(concessionaria).name and conta.nome_tipo_servico == ServiceTypeEnum(tipo_servico).name

        for conta in self._paid_bills:
            if (achou(conta)):
                return conta

        return None

    @property
    def count(self) -> int:
        return len(self._paid_bills)
