from dataclasses import dataclass
import os
from typing import List, Any
import io
import pandas as pd
from src.domain.enums.service_type_enum import ServiceTypeEnum
from src.infra.google_drive_handler.google_drive_handler import GoogleDriveHandler
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
        if (name == '#NOS'):
            return ServiceProviderEnum.NOS

        return ServiceProviderEnum.DESCONHECIDO

    def __init__(self):
        self._accommodations = []

    def _get_providers_name(self, df) -> List[str]:
        columns = []
        for name, value in df.iteritems():
            if (len(name) > 1) and (name[0] == '#'):
                columns.append(name)
        return columns

    def from_excel(self, stream_file: Any)  -> None:
        df_ = pd.read_excel(io.BytesIO(stream_file), sheet_name="#LISTA_GERAL")
        df = df_.where(pd.notnull(df_), None)
        providers_name = self._get_providers_name(df)

        for row in range(df.shape[0]):
            if row == 0:
                continue

            if df.iat[row, 1] is None:
                break

            acc_aux = Accommodation2(id=df.iat[row, 1], start_date=df.iat[row, 2], nif_title=df.iat[row, 3], folder_id=df.iat[row, 4], folder_accounting_id=df.iat[row, 5])
            acc_aux.add_service_type(ServiceTypeStatus(ServiceTypeEnum.AGUA, df.iat[row, 4]))
            acc_aux.add_service_type(ServiceTypeStatus(ServiceTypeEnum.TELECOM, df.iat[row, 5]))
            acc_aux.add_service_type(ServiceTypeStatus(ServiceTypeEnum.LUZ, df.iat[row, 6]))

            #print(f'#CLIENT_ID {df.iat[row, 1] }')
            #print(f'#DATA_LANÇAMENTO {df.iat[row, 2] }')
            #print(f'#NIF_TITULAR {df.iat[row, 3] }')
            #print(f'#ÁGUA {df.iat[row, 4] }')
            #print(f'#COMUNICAÇÕES {df.iat[row, 5] }')
            #print(f'#ENERGIA {df.iat[row, 6] }')
            #print(f'#LINK_DRIVE {df.iat[row, 7] }')
            #print(f'#LINK_CONSOLIDAÇÃO {df.iat[row, 8] }')

            for indx, name in enumerate(providers_name):
                contract_aux = Contract(id_service_provide=self._str_2_provider(name),
                                        cliente=df.iat[row, 9 + (7 * indx)],
                                        conta=df.iat[row, 10 + (7 * indx)],
                                        contrato=df.iat[row, 11 + (7 * indx)],
                                        local_consumo=df.iat[row, 12 + (7 * indx)],
                                        instalacao=df.iat[row, 13 + (7 * indx)],
                                        referencia=df.iat[row, 14 + (7 * indx)],
                                        servico=df.iat[row, 15 + (7 * indx)])

                if (contract_aux.is_valid()):
                    acc_aux.add_contract(contract_aux)
                    #print(f'{name} #CLIENTE {df.iat[row, 9 + (7 * indx)]}')
                    #print(f'{name} #CONTA {df.iat[row, 10 + (7 * indx)]}')
                    #print(f'{name} #CONTRATO {df.iat[row, 11 + (7 * indx)]}')
                    #print(f'{name} #LOCAL_CONSUMO {df.iat[row, 12 + (7 * indx)]}')
                    #print(f'{name} #INSTALAÇÃO {df.iat[row, 13 + (7 * indx)]}')
                    #print(f'{name} #REFERENCIA {df.iat[row, 14 + (7 * indx)]}')
                    #print(f'{name} #SERVIÇO {df.iat[row, 15 + (7 * indx)]}')

            self._accommodations.append(acc_aux)

    def get(self, concessionaria, cliente: str, conta: str, local: str) -> Accommodation2:
        def filtro(el: Accommodation2):
            teve_teste = False
            if el.cliente and cliente:
                teve_teste = True
                if el.cliente != cliente:
                    return False

            if el.conta and conta:
                teve_teste = True
                if el.conta != conta:
                    return False

            if el.local and local:
                teve_teste = True
                if el.local != local:
                    return False

            return teve_teste

        for acc in self._accommodations:
            for conta in acc._contracts:
                if filtro(conta):
                    return conta

        return None
