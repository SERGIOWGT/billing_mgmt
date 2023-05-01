from dataclasses import dataclass
from src.domain.enums.service_provider_enum import ServiceProviderEnum


@dataclass
class Accommodation:
    concessionaria: ServiceProviderEnum
    nome: str = ''
    diretorio: str = ''
    nif: str = ''
    cliente: str = ''
    conta: str = ''
    local: str = ''
