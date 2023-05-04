from dataclasses import dataclass
from src.domain.enums import ServiceProviderEnum, AccommodationStatusEnum


@dataclass
class Accommodation:
    concessionaria: ServiceProviderEnum
    status: AccommodationStatusEnum
    nome: str = ''
    diretorio: str = ''
    nif: str = ''
    cliente: str = ''
    conta: str = ''
    local: str = ''
