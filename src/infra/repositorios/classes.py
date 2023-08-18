from dataclasses import dataclass
import datetime
from typing import List
from src.domain.enums import ServiceProviderEnum, ServiceTypeEnum

@dataclass
class ServiceTypeStatus:
    _id_service_type: ServiceTypeEnum
    _status: str

    def __init__(self, id_status_type, status):
        self._id_service_type = id_status_type
        self._status = status

@dataclass
class Contract:
    _id_service_provide: ServiceProviderEnum
    _servico: str = ''

    def __init__(self, id_service_provide: ServiceProviderEnum, cliente: str, conta: str, contrato: str, local_consumo: str, instalacao: str, referencia: str, servico: str) -> None:
        def str_to_vet(str_data)-> List[str]:
            if str_data:
                str_data = str_data.strip()
            return str_data.split(';') if str_data else []

        self._id_service_provide = id_service_provide

        self._vet_cliente = str_to_vet(cliente)
        self._vet_conta = str_to_vet(conta)
        self._vet_contrato = str_to_vet(contrato)
        self._vet_local_consumo = str_to_vet(local_consumo)
        self._vet_instalacao = str_to_vet(instalacao)
        self._vet_referencia = str_to_vet(referencia)
        self._vet_servico = str_to_vet(servico)

    def is_valid(self) -> bool:
        if len(self._vet_cliente)>0:
            return True
        if len(self._vet_conta)>0:
            return True
        if len(self._vet_contrato) > 0:
            return True
        if len(self._vet_local_consumo) > 0:
            return True
        if len(self._vet_instalacao) > 0:
            return True

        return False

    def is_you(self, concessionaria: ServiceProviderEnum, cliente: str, conta: str, contrato: str, local: str, instalacao: str) -> bool:
        if self._id_service_provide != concessionaria:
            return False

        teve_teste = False
        if len(self._vet_cliente) > 0 and cliente:
            teve_teste = True
            if cliente not in self._vet_cliente:
                return False
        if len(self._vet_conta) > 0 and conta:
            teve_teste = True
            if conta not in self._vet_conta:
                return False
        if len(self._vet_contrato) > 0 and contrato:
            teve_teste = True
            if contrato not in self._vet_contrato:
                return False
        if len(self._vet_instalacao) > 0 and instalacao:
            teve_teste = True
            if instalacao not in self._vet_instalacao:
                return False
        if len(self._vet_local_consumo) > 0 and local:
            teve_teste = True
            if local not in self._vet_local_consumo:
                return False

        return teve_teste
    
class Accommodation2:
    _id = ''
    _start_date: datetime = None
    _end_date: datetime = None
    _nif_title = ''
    _folder_id = ''
    _folder_accounting_id = ''
    _folder_setup_id = ''
    _services_type: List[ServiceTypeStatus] = None
    _contracts: List[Contract] = None
    _status_fecho = {}
    _line: int = 0

    def __init__(self, id: str, start_date: datetime, end_date: datetime, nif_title: str, folder_id: str, folder_accounting_id: str, folder_setup_id: str, line: int, status_fecho: dict) -> None:
        self._id = id
        self._start_date = start_date
        self._end_date = end_date
        self._nif_title = nif_title
        self._folder_id = folder_id
        self._folder_accounting_id = folder_accounting_id
        self._folder_setup_id = folder_setup_id
        self._contracts = []
        self._services_type: List[ServiceTypeStatus] = []
        self._status_fecho = status_fecho
        self._line = line

    def add_contract(self, contract: Contract) -> None:
        self._contracts.append(contract)

    @property
    def number_of_contracts(self) -> int:
        return len(self._contracts)

    def add_service_type(self, service_type_status: ServiceTypeStatus) -> None:
        self._services_type.append(service_type_status)

    def in_setup(self, data: datetime) -> bool:
        if self._start_date.year == 2050:
            return True

        return self._start_date > data

    def is_terminated(self, data: datetime) -> bool:
        return self._end_date < data

    def is_closed(self, data: datetime) -> bool:
        str_data = f'{data.year}.{data.month}'
        ret = self._status_fecho.get(str_data, 0)
        return ret != 0

    def is_must_accounting(self, service_type: ServiceTypeEnum):
        for el in self._services_type:
            if el._id_service_type == service_type:
                return el._status == 1  # Um

        return False
