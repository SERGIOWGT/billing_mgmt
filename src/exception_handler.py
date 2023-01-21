class ApplicationException(Exception):
    @staticmethod
    def when(condicao: bool, mensagem: str) -> None:
        if condicao:
            raise ApplicationException(mensagem)
