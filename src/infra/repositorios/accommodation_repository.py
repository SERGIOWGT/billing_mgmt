from dataclasses import dataclass
from typing import List, Any
import io
import pandas as pd
from datetime import datetime
from src.domain.enums.service_type_enum import ServiceTypeEnum
from src.infra.repositorios.classes import Accommodation2, Contract, ServiceTypeStatus
from src.domain.enums.service_provider_enum import ServiceProviderEnum


@dataclass
class AccommodationRepository:
    _accommodations: Accommodation2 = None

    def _str_2_provider(self, name: str) -> str:
        name = name.upper()
        if (name == '#EDP'):
            return ServiceProviderEnum.EDP
        if (name == '#GALP'):
            return ServiceProviderEnum.GALP
        if (name == '#AGUAS_PORTO'):
            return ServiceProviderEnum.AGUAS_DE_PORTO
        if (name == '#AGUAS_GAIA'):
            return ServiceProviderEnum.AGUAS_DE_GAIA
        if (name == '#ALTICE'):
            return ServiceProviderEnum.ALTICE_MEO
        if (name == '#VODAFONE'):
            return ServiceProviderEnum.VODAFONE
        if (name == '#GOLD_ENERGY'):
            return ServiceProviderEnum.GOLDEN_ENERGY
        if (name == '#EPAL'):
            return ServiceProviderEnum.EPAL
        if (name == 'EPAL'):
            return ServiceProviderEnum.EPAL
        if (name == '#NOS'):
            return ServiceProviderEnum.NOS
        if (name == 'NOS'):
            return ServiceProviderEnum.NOS

        return ServiceProviderEnum.DESCONHECIDO

    def __init__(self):
        self._accommodations = []

    def _get_providers_name(self, df) -> List[str]:
        columns = []
        for name, value in df.iteritems():
            # a = 0
            if len(name) > 1 and name[0] == '#':
                columns.append(name)
        return columns

    def from_excel(self, stream_file: Any) -> None:
        def get_el(value):
            return '' if value == 'None' else value

        df_ = pd.read_excel(io.BytesIO(stream_file), sheet_name="#ESTADO_FECHO")
        df = df_.where(pd.notnull(df_), None)

        base_year = df.columns[2]
        temp_fecho_columns = []
        for year in range(base_year, base_year+2):
            for month in range(1, 13):
                temp_fecho_columns.append(f'{year}.{month}')

        temp_estado_fecho = {}
        for row in range(df.shape[0]):
            if row == 0:
                continue

            line = df.iat[row, 0]
            if line is None:
                break

            id_alojamento = df.iat[row, 1]
            if id_alojamento is None:
                continue

            datas = {}
            for col, col_name in enumerate(temp_fecho_columns):
                value = str(df.iat[row, col+2])
                value = value.replace('.0', '')
                if value.isnumeric():
                    datas[col_name] = int(value)
                else:
                    datas[col_name] = 0

            temp_estado_fecho[id_alojamento] = datas

        df_ = pd.read_excel(io.BytesIO(stream_file), sheet_name="#LISTA_GERAL")
        df = df_.where(pd.notnull(df_), None)
        providers_name = self._get_providers_name(df)

        for row in range(df.shape[0]):
            if row == 0:
                continue

            line = df.iat[row, 0]
            if line is None:
                break

            id_alojamento = df.iat[row, 1]
            if id_alojamento is None:
                continue
            
            folder_id = df.iat[row, 7]
            if (folder_id):
                folder_id = str(folder_id).replace('https://drive.google.com/drive/folders/', '')
                folder_id = folder_id.replace('?usp=drive_link', '')

            folder_accounting_id = df.iat[row, 8]
            if (folder_accounting_id):
                folder_accounting_id = str(folder_accounting_id).replace('https://drive.google.com/drive/folders/', '')
                folder_accounting_id = folder_accounting_id.replace('?usp=drive_link', '')

            start_date = df.iat[row, 2]
            if (isinstance(start_date, datetime) is False):
                start_date = datetime(2050, 1, 1)

            status_fecho = temp_estado_fecho[id_alojamento]
            acc_aux = Accommodation2(id=df.iat[row, 1], start_date=start_date, nif_title=df.iat[row, 3], folder_id=folder_id,
                                     folder_accounting_id=folder_accounting_id, line=line, status_fecho=status_fecho)
            acc_aux.add_service_type(ServiceTypeStatus(ServiceTypeEnum.AGUA, df.iat[row, 4]))
            acc_aux.add_service_type(ServiceTypeStatus(ServiceTypeEnum.TELECOM, df.iat[row, 5]))
            acc_aux.add_service_type(ServiceTypeStatus(ServiceTypeEnum.LUZ, df.iat[row, 6]))

            for indx, name in enumerate(providers_name):
                cliente = get_el(str(df.iat[row, 9 + (7 * indx)]))
                conta = get_el(str(df.iat[row, 10 + (7 * indx)]))
                contrato = get_el(str(df.iat[row, 11 + (7 * indx)]))
                local_consumo = get_el(str(df.iat[row, 12 + (7 * indx)]))
                instalacao = get_el(str(df.iat[row, 13 + (7 * indx)]))
                referencia = get_el(str(df.iat[row, 14 + (7 * indx)]))
                servico = get_el(str(df.iat[row, 15 + (7 * indx)]))

                contract_aux = Contract(id_service_provide=self._str_2_provider(name),
                                        cliente=cliente,
                                        conta=conta,
                                        contrato=contrato,
                                        local_consumo=local_consumo,
                                        instalacao=instalacao,
                                        referencia=referencia,
                                        servico=servico)

                if (contract_aux.is_valid()):
                    acc_aux.add_contract(contract_aux)

            if (acc_aux.number_of_contracts > 0):
                self._accommodations.append(acc_aux)

    def get(self, concessionaria, cliente: str, conta: str, contrato: str, local: str, instalacao: str) -> Accommodation2:
        def filtro(el: Contract):
            teve_teste = False
            if el._cliente and cliente:
                teve_teste = True
                if el._cliente != cliente:
                    return False
            if el._conta and conta:
                teve_teste = True
                if el._conta != conta:
                    return False
            if el._contrato and contrato:
                teve_teste = True
                if el._contrato != contrato:
                    return False

            if el._instalacao and instalacao:
                teve_teste = True
                if el._instalacao != instalacao:
                    return False
            if el._local_consumo and local:
                teve_teste = True
                if el._local_consumo != local:
                    return False

            return teve_teste

        for acc in self._accommodations:
            if acc._id == 'LA_Pia24A_2Es':
                a = 0

            contas = [x for x in acc._contracts if x._id_service_provide == concessionaria]
            for el in contas:
                if filtro(el):
                    return acc

        return None
