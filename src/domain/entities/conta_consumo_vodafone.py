
from datetime import date, datetime
from unidecode import unidecode

from src.domain.enums import (ConcessionariaEnum, TipoDocumentoEnum,
                              TipoServicoEnum)

from .base.conta_consumo_base import ContaConsumoBase


class ContaConsumoVodafone(ContaConsumoBase):
    def __init__(self):
        super().__init__()
        self.concessionaria = ConcessionariaEnum.VODAFONE
        self.tipo_servico = TipoServicoEnum.TELECOM

    def _set_unavaible_data(self) -> None:
        self.id_cliente = ''
        self.local_consumo = ''

    def _search_id_data(self, text) -> bool:
        informacoes_cliente = self._get_data(text, 'No Documento No Contribuinte No de Conta', 'Apoio a').split()
        if (len(informacoes_cliente) != 4):
            return False

        self.id_documento = informacoes_cliente[1]
        self.id_contrato = informacoes_cliente[3]
        self.id_contribuinte = informacoes_cliente[2]
        
    def _str_2_date(self, value: str) -> date:
        _dt_retorno = None
        if (value):
            try:
                _dt_retorno = datetime.strptime(value, '%Y/%m/%d')
            except Exception:
                _dt_retorno = None
        return _dt_retorno

    def _get_periodo_faturacao(self, text) -> None:
        self.periodo_referencia = self._get_data(text, 'Periodo de faturacao:', '\r\n')
        if (self.periodo_referencia == ''):
            return

        dt_aux = self._str_2_date(self.str_emissao)
        if dt_aux is None:
            return

        self.periodo_referencia = self.periodo_referencia.replace(' a ', ' ')
        vet = self.periodo_referencia.strip().split(' ')
        if (len(vet) != 4):
            return

        mes_emissao = dt_aux.month
        ano_emissao = dt_aux.year

        vet[1] = self.mes_extenso.get(vet[1], '')
        vet[3] = self.mes_extenso.get(vet[3], '')
        if mes_emissao == 12:
            self.periodo_referencia = f'{ano_emissao-1}/{vet[1]}/{vet[0]} ~ {ano_emissao-1}/{vet[3]}/{vet[2]}'
        elif mes_emissao == 1:
            self.periodo_referencia = f'{ano_emissao-1}/{vet[1]}/{vet[0]} ~ {ano_emissao}/{vet[3]}/{vet[2]}'
        else:
            self.periodo_referencia = f'{ano_emissao}/{vet[1]}/{vet[0]} ~ {ano_emissao}/{vet[3]}/{vet[2]}'

    def _get_data_vencimento(self, text) -> None:
        self.str_vencimento = self._get_data(text, 'Data limite de pagamento:', 'Valor deste mes').strip()
        if not self.str_vencimento:
            self.str_vencimento = self._get_data(text, 'Debito a partir de', 'Valor deste mes').strip()

    def create(self, text: str) -> None:
        text = unidecode(text)

        self._set_unavaible_data()
        self._check_account_of_qqd(text.upper())
        self.str_emissao = self._get_data(text, 'Data de emissao: ', ' Periodo de fatura')
        self.str_emissao = self._convert_2_default_date(self.str_emissao, 'DMY')
        self._get_periodo_faturacao(text)
        self._get_data_vencimento(text)

        if self._search_id_data(text) is False:
            if ('Detalhe da fatura de' in text):
                self.tipo_documento = TipoDocumentoEnum.DETALHE_FATURA
                self.str_erro = 'Detalhe da Fatura VodaFone'
                return

        valor = self._get_data(text, 'Total da fatura com IVA', 'Resumo do IVA').split('EUR')
        self.str_valor = valor[-1]

        self.str_vencimento = self._convert_2_default_date(self.str_vencimento, 'DMY', full_month=True)
        self._adjust_data()
