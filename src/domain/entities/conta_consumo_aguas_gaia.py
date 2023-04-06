from unidecode import unidecode
from src.domain.enums import ConcessionariaEnum, TipoServicoEnum
from .conta_consumo_base import ContaConsumoBase


class ContaConsumoAguasDeGaia(ContaConsumoBase):
    def __init__(self):
        super().__init__(self)
        self.concessionaria = ConcessionariaEnum.AGUAS_DE_GAIA
        self.tipo_servico = TipoServicoEnum.AGUA

    def create(self, text: str) -> None:
        text = unidecode(text)

        # OK
        cliente_conta = self._get_data(text, 'Cliente / Conta:', '\r\n')
        vet = cliente_conta.strip().split('/')
        if (len(vet) == 2):
            self.id_cliente = vet[0]
            self.id_contrato = cliente_conta

        self.local_consumo = self._get_data(text, 'Local Consumo:', '\r\n')
        self.id_contribuinte = self._get_data(text, 'NIF:', '\r\n')
        self.str_vencimento = self._get_data(text, 'Debito a partir de\r\n', '\r\n')
        if (self.str_vencimento == ''):
            self.str_vencimento = self._get_data(text, 'Data limite pagamento\r\n', '\r\n')
            
        self.str_emissao = self._get_data(text, 'Data de Emissao\r\n', '\r\n')

        self.periodo_referencia = self._get_data(text, 'Periodo Faturacao:', '\r\n')

        # WARN: id_documento Tem mas esta colado no campo titular da conta
        self.id_documento = self._get_data(text, 'Titular da conta:\r\n', '\r\n')

        # WARN: valor
        vet = self._get_data(text, 'Saldo Atual', '\r\n')
        vet = vet.strip()
        vet = vet.split(' ')
        if (len(vet) == 2):
            self.str_valor = vet[1]

        # Ajusta as datas
        self.str_emissao = self._convert_2_default_date(self.str_emissao, 'DMY', full_month=True)
        self.str_vencimento = self._convert_2_default_date(self.str_vencimento, 'DMY', full_month=True)

        self._adjust_data()
