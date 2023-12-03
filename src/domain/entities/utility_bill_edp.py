import re
from unidecode import unidecode
from src.domain.enums import ServiceProviderEnum, ServiceTypeEnum, DocumentTypeEnum
from .base.base_utility_bill import UtilityBillBase


class UtilityBillEDP(UtilityBillBase):
    def __init__(self):
        super().__init__(self)
        self.concessionaria = ServiceProviderEnum.EDP
        self.tipo_servico = ServiceTypeEnum.LUZ

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

    def _get_local_consumo(self, text) -> None:
        self.local_consumo = ''

    def _get_id_contribuinte(self, text) -> None:
        self.id_contribuinte = ''

    def _get_id_cliente(self, text) -> None:
        self.id_cliente = ''

    def _get_id_contrato(self, text: str):
        start_pos = 0
        start_pos = text.find('meus dados')
        if start_pos <= 0:
            return ''

        str_aux = 'digo de contrato'
        start_pos = text.find(str_aux, start_pos+len(str_aux)+1)
        if start_pos <= 0:
            str_aux = 'digo do contrato'
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

        self.id_contrato = id_contrato

    def _get_periodo_faturacao(self, text):

        # Remove espaços extras do texto
        #text = re.sub(r"\s+", " ", text)

        # Extrai as informações desejadas do texto
        #_re_aux = re.search(r"Periodo de faturacao: (.*)\r\n", text)
        #if _re_aux is None:
        #cliente = _re_aux.group(1)
        
        self.periodo_referencia = self._conv_periodo_faturacao(self._get_data(text, 'Periodo de faturacao:', '\r\n'))
        A = 0

    def _get_id_documento(self, text: str) -> None:
        self.id_documento = self._get_data(text, 'EDPC801-', '\r\n')
        if (self.id_documento == ''):
            self.id_documento = self._get_data(text, 'EDPC805-', '\r\n')

    def _get_data_vencimento(self, text) -> None:
        self.str_vencimento = self._get_data(text, 'conta a partir de:\r\n', '\r\n')
        if (self.str_vencimento == ''):
            self.str_vencimento = self._get_data(text, 'posso\r\npagar?\r\n', '\r\n')
        self.str_vencimento = self._convert_2_default_date(self.str_vencimento, 'DMY', full_month=True)

    def _get_valor(self, text) -> None:
        self.str_valor = self._get_data(text, 'a pagar?\r\n', '\r\n')
        if self.str_valor == '':
            self.str_valor = self._get_data(text, 'a receber?\r\n', '\r\n')
            if self.str_valor:
                self.tipo_documento = DocumentTypeEnum.NOTA_CREDITO

    def _get_data_emissao(self, text) -> None:
        self.str_emissao = self._get_data(text, 'Documento emitido a:', '\r\n')
        self.str_emissao = self._convert_2_default_date(self.str_emissao, 'DMY', full_month=True)

    def create(self, text: str) -> None:
        text = unidecode(text)

        self._get_periodo_faturacao(text)
        self._get_local_consumo(text)
        self._get_id_cliente(text)
        self._get_id_contrato(text)
        self._get_id_documento(text)
        self._get_data_emissao(text)
        self._get_data_vencimento(text)
        self._get_valor(text)
        self._check_account_of_qqd(text.upper())
        self._adjust_data()
