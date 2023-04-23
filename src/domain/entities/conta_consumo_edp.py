from unidecode import unidecode
from src.domain.enums import ConcessionariaEnum, TipoServicoEnum
from .base.conta_consumo_base import ContaConsumoBase


class ContaConsumoEDP(ContaConsumoBase):
    def __init__(self):
        super().__init__(self)
        self.concessionaria = ConcessionariaEnum.EDP
        self.tipo_servico = TipoServicoEnum.TELECOM

    def _conv_periodo_faturacao(self, value: str):
        ret = ''
        if (value):
            ret = value.strip()
            ret = ret.replace(' a ', '~')
            ret = ret.replace(' de ', '.')
            ret = ret.replace(' ', '.')
            vet_datas = ret.split('~')
            if (len(vet_datas) == 2):
                vet_data_aberta = vet_datas[0].split('.')
                if (len(vet_data_aberta) == 2):
                    vet_data_aberta = vet_datas[1].split('.')
                    vet_datas[0] += '.'+vet_data_aberta[2]

                vet_datas[0] = self._convert_2_default_date(vet_datas[0], 'DMY', True)
                vet_datas[1] = self._convert_2_default_date(vet_datas[1], 'DMY', True)
                if vet_datas[0] != '' and vet_datas[1] != '':
                    ret = f'{vet_datas[0]} ~ {vet_datas[1]}'

        return ret

    def _get_id_contrato(self, text: str):
        start_pos = 0
        start_pos = text.find('meus dados')
        if start_pos <= 0:
            return ''

        str_aux = 'digo de contrato'
        start_pos = text.find(str_aux, start_pos+len(str_aux)+1)
        if start_pos <= 0:
            return ''

        str_aux = '\r\n'
        end_pos = text.find(str_aux, start_pos+len(str_aux)+1)
        if end_pos <= 0:
            return ''
        new_pos = end_pos + len(str_aux)
        id_contrato = ''
        contador = new_pos
        while ((id_contrato+text[contador]).isnumeric()):
            id_contrato += text[contador]
            contador += 1

        return id_contrato

    def _set_unavaible_data(self) -> None:
        self.id_contribuinte = ''
        self.id_cliente = ''
        self.local_consumo = ''

    def _get_data_vencimento(self, text) -> None:
        self.str_vencimento = self._get_data(text, 'conta a partir de:\r\n', '\r\n')
        if (self.str_vencimento == ''):
            self.str_vencimento = self._get_data(text, 'posso\r\npagar?\r\n', '\r\n')

    def create(self, text: str) -> None:
        text = unidecode(text)

        self._set_unavaible_data()
        self._get_data_vencimento(text)
        self._check_account_of_qqd(text.upper())

        self.id_contrato = self._get_id_contrato(text)
        self.id_documento = self._get_data(text, 'EDPC801-', '\r\n')
        self.periodo_referencia = self._conv_periodo_faturacao(self._get_data(text, 'Periodo de faturacao:', '\r\n'))
        self.str_emissao = self._get_data(text, 'Documento emitido a:', '\r\n')
        self.str_valor = self._get_data(text, 'a pagar?\r\n', '\r\n')

        # Ajusta as datas
        self.str_emissao = self._convert_2_default_date(self.str_emissao, 'DMY', full_month=True)
        self.str_vencimento = self._convert_2_default_date(self.str_vencimento, 'DMY', full_month=True)

        self._adjust_data()
    