from dataclasses import dataclass
from enum import IntEnum

class ConcessionariaEnum(IntEnum):
    NOS = 1
    MEO = 2
    AGUAS_DE_GAIA = 3
    EDP = 4
    VODAFONE = 5
    ALTICE = 6

class TipoServicoEnum(IntEnum):
    AGUA = 1
    LUZ = 2
    INTERNET = 3

@dataclass
class ContaConsumo:
    concessionaria: ConcessionariaEnum
    tipo_servico: TipoServicoEnum
    data_emissao = ''
    data_vencimento = ''
    valor = ''
    id_contribuinte = ''
    id_cliente = ''
