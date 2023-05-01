from enum import IntEnum


class DocumentTypeEnum(IntEnum):
    DESCONHECIDO = 0
    CONTA_CONSUMO = 1
    NOTA_CREDITO = 2
    DETALHE_FATURA = 3
    FATURA_ZERADA = 4
