#
# CLASSE DESENVOLVIDA EM COMO REPOSITORIO (REPOSITORY PATTERN) DOS OBJETOS DAS CONTAS PROCESSADAS NA PLANIHLA DE HISTORICO
#

from dataclasses import dataclass
from datetime import datetime
import os
from typing import List
import pandas as pd
from pyparsing import Any
from itertools import groupby
from src.domain.entities.paid_utility_bill import PaidUtilityBill
from src.domain.enums import ServiceProviderEnum, ServiceTypeEnum

from src.infra.handlers.exception_handler import ApplicationException

@dataclass
class PaidBillRepository:
    _paid_bills: List[PaidUtilityBill] = None

    def __init__(self):
        self._paid_bills = []

    def number_of_payments(self) -> int:
        return len(self._paid_bills)

    def get_last_discontinuous_period(self) -> Any:
        ret = []
        work_list = [x for x in self._paid_bills if x.nome_tipo_documento in ('CONTA_CONSUMO', 'FATURA_ZERADA', 'NOTA_CREDITO')]
        work_list.sort(key=lambda x: (x.nome_Accommodation, x.nome_concessionaria, x.dt_emissao))

        old_key = ''
        dt_old_end_ref = ''
        for el in work_list:
            new_key = f'{el.nome_Accommodation}+{el.nome_concessionaria}+{el.nome_tipo_servico}'
            if old_key != new_key:
                old_key = new_key
                dt_old_end_ref = el.dt_end_ref
                continue

            if el.dt_begin_ref and dt_old_end_ref and (el.dt_begin_ref != dt_old_end_ref):
                _dt_begin_ref = datetime.strptime(el.dt_begin_ref, "%Y/%m/%d")
                _old_end_date_ref = datetime.strptime(dt_old_end_ref, "%Y/%m/%d")
                if abs((_old_end_date_ref - _dt_begin_ref).days) > 1:
                    ret.append(f'{el.nome_Accommodation}, {el.nome_concessionaria}, {el.nome_tipo_servico}, entre as datas {dt_old_end_ref} e {el.dt_begin_ref}')
            dt_old_end_ref = el.dt_end_ref
            
        return ret

    def get_possible_faults(self, days: int) -> Any:
        work_list = [x for x in self._paid_bills if x.nome_tipo_documento in ('CONTA_CONSUMO', 'FATURA_ZERADA', 'NOTA_CREDITO')]
        work_list.sort(key=lambda x: (x.nome_Accommodation, x.nome_concessionaria))

        ret = []
        for key, group in groupby(work_list, key=lambda x: (x.nome_Accommodation, x.nome_concessionaria)):
            nome_Accommodation, nome_concessionaria = key
            max_date = max(item.dt_emissao for item in group)
            if abs((datetime.strptime(max_date, "%Y/%m/%d") - datetime.now()).days) > days:
                ret.append(f'{nome_Accommodation}, {nome_concessionaria}, ultima conta emitida em {max_date}')

        return ret

    def from_excel(self, file_path: Any) -> None:
        if not os.path.exists(file_path):
            return

        df_ = pd.read_excel(file_path, dtype={'N. Documento / N. Fatura': object})
        df = df_.where(pd.notnull(df_), None)
        cols = df.shape[1]
        ApplicationException.when(cols != 22, 'History Sheet must have 22 columns. ')
        expected_columns = ['QQ Destino', 'Alojamento', 'Ano Emissao', 'Mes Emissao', 'Concessionaria', 'Tipo Servico',
                            'Tipo Documento', 'N. Contrato', 'N. Cliente', 'N. Contribuinte', 'Local Consumo', 'Instalacao',
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
            dt_begin_ref = row['Inicio Referencia']
            dt_end_ref = row['Fim Referencia']
            nome_tipo_documento = row['Tipo Documento']

            self._paid_bills.append(PaidUtilityBill(provider_service_name, service_type_name, accommodation_name,
                                    id_documento, dt_emissao, original_file_id, dt_begin_ref, dt_end_ref,nome_tipo_documento))

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
