from dataclasses import dataclass
import datetime
from typing import List
from src.domain.enums.service_provider_enum import ServiceProviderEnum
from src.domain.enums.service_type_enum import ServiceTypeEnum


dataclass
class ServiceTypeStatus:
    _id_service_type: ServiceTypeEnum
    _status: str

    def __init__(self, id_status_type, status):
        self._id_service_type = id_status_type
        self._status = status

@dataclass
class Contract:
    _id_service_provide: ServiceProviderEnum
    _cliente: str = ''
    _conta: str = ''
    _contrato: str = ''
    _local_consumo: str = ''
    _instalacao: str = ''
    _referencia: str = ''
    _servico: str = ''

    def __init__(self, id_service_provide: ServiceProviderEnum, cliente: str, conta: str, contrato: str, local_consumo: str, instalacao: str, referencia: str, servico: str) -> None:
        self._id_service_provide = id_service_provide
        self._cliente = cliente
        self._conta = conta
        self._contrato= contrato
        self._local_consumo = local_consumo
        self._instalacao = instalacao
        self._referencia = referencia
        self._servico = servico

    def is_valid(self) -> bool:
        if self._cliente is not None:
            return True
        if self._conta is not None:
            return True
        if self._contrato is not None:
            return True
        if self._local_consumo is not None:
            return True

        return False

class Accommodation2:
    _id = ''
    _start_date: datetime = None
    _nif_title = ''
    _folder_id = ''
    _folder_accounting_id = ''
    _services_type: List[ServiceTypeStatus] = None
    _contracts: List[Contract] = None

    def __init__(self, id: str, start_date: datetime, nif_title: str, folder_id: str, folder_accounting_id: str) -> None:
        self._id = id
        self._start_date = start_date
        self._nif_title = nif_title
        self._folder_id = folder_id
        self._folder_accounting_id = folder_accounting_id
        self._contracts = []
        self._services_type = []

    def add_contract(self, contract: Contract) -> None:
        self._contracts.append(contract)

    def add_service_type(self, service_type_status: ServiceTypeStatus) -> None:
        self._services_type.append(service_type_status)
