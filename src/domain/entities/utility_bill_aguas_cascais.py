import re
from unidecode import unidecode
from src.domain.enums import ServiceProviderEnum, ServiceTypeEnum
from .base.base_utility_bill import UtilityBillBase


class UtilityBillAguasDeCascais(UtilityBillBase):
		def __init__(self):
			super().__init__(self)
			self.concessionaria = ServiceProviderEnum.AGUAS_DE_CASCAIS
			self.tipo_servico = ServiceTypeEnum.AGUA

		def _convert_data(self, str_data: str, format: str) -> str:
			if (not str_data):
				return ''

			return str_data

		def _get_local_consumo(self, text) -> None:
			text_aux = re.search(r'\r\n(\d+)\r\nCLIENTE No:', text)
			if text_aux:
				text_aux = text_aux.group(1)
				regex_patern = r'\r\n(\d+)\r\n' + re.escape(text_aux) + r'\r\nCLIENTE No:'
				text_aux = re.search(regex_patern, text)
				if text_aux:
					self.local_consumo = text_aux.group(1)

		def _get_id_contribuinte(self, text) -> None:
				self.id_contribuinte = ''

		def _get_id_cliente(self, text) -> None:
			text_aux = re.search(r'CLIENTE No: (\d+)\r\n', text)
			if text_aux:
				self.id_cliente = text_aux.group(1)

		def _get_id_contrato(self, text) -> None:
			pass
				#self.id_contrato = self._get_data(text, 'CONTA CLIENTE No', '\r\n')

		def _get_periodo_faturacao(self, text):
				self.periodo_referencia = self._get_data(text, 'COMUNIQUE A SUA LEITURA DE', '\r\n')
				self.periodo_referencia = self.periodo_referencia.replace(' a ', '~')
				self.periodo_referencia = self.periodo_referencia.replace('.', '-')

		def _get_id_documento(self, text: str) -> None:
			self.id_documento = self._get_data(text, '\r\nFT', '\r\nData de Emiss')

		def _get_data_vencimento(self, text) -> None:
			self.str_vencimento = self._get_data(text, 'A PAGAR ATE ', '\r\n')
			self.str_vencimento = self._convert_2_default_date(self.str_vencimento, 'DMY')

		def _get_valor(self, text) -> None:
			self.str_valor = self._get_data(text, 'TOTAL A PAGAR', 'EUR')

		def _get_data_emissao(self, text) -> None:
			# WARN: data de emissao depende do id_documento
			self.str_emissao = text[1:11]
			self.str_emissao = self._convert_2_default_date(self.str_emissao, 'DMY')

		def create(self, text: str) -> None:
			text = unidecode(text)
			self._get_periodo_faturacao(text)
			self._get_id_cliente(text)
			self._get_local_consumo(text)
			# self._get_id_contrato(text)
			self._get_id_documento(text)
			self._get_data_emissao(text)
			self._get_data_vencimento(text)
			self._get_valor(text)
			self._check_account_of_qqd(text.upper())
			self._adjust_data()
