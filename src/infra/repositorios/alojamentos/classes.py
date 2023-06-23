import datetime
from typing import List
from src.domain.enums.service_provider_enum import ServiceProviderEnum

class Contract:
    _id_service_provide: ServiceProviderEnum
    diretorio: str = ''
    nif: str = ''
    cliente: str = ''
    conta: str = ''
    local: str = ''


class Accommodation2:
    _id = ''
    _start_date: datetime
    _nif_title: str
    _services_type_title: List[str]
    _folder_id: str
    _folder_accounting_id: str
    _contracts: List[Contract]
