from typing import Any


class ApplicationException(Exception):
    @staticmethod
    def when(condicao: bool, mensagem: str, logger:Any=None) -> None:
        if condicao:
            if (logger):
                logger.error(mensagem)
            raise ApplicationException(mensagem)
