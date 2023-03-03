from unidecode import unidecode
from src.domain.models.conta_consumo import ConcessionariaEnum, ContaConsumo, TipoServicoEnum
from .extrator_conta_base import ExtratorContaConsumoBase

class ExtratorContaConsumoVodafone(ExtratorContaConsumoBase):
    def get_info(self, text: str) -> ContaConsumo:
        text = unidecode(text)
        conta_consumo = ContaConsumo(concessionaria=ConcessionariaEnum.VODAFONE, tipo_servico=TipoServicoEnum.INTERNET)

        # OK
        conta_consumo.id_cliente = 'N/A'
        
        informacoes_cliente = self.get_data(text, 'No Documento No Contribuinte No de Conta', 'Apoio a').split()
        if (len(informacoes_cliente) == 4):
            conta_consumo.id_documento = informacoes_cliente[1]
            conta_consumo.id_contrato = informacoes_cliente[3]
            conta_consumo.id_contribuinte = informacoes_cliente[2]
        else:
            conta_consumo.id_documento = 'N/A'
            conta_consumo.id_contrato = 'N/A'
            conta_consumo.id_contribuinte = 'N/A'
            
        conta_consumo.data_emissao = self.get_data(text, 'Data de emissao: ', num_chars=10)
        valor = self.get_data(text, 'Total da fatura com IVA', 'Resumo do IVA').split('EUR')
        conta_consumo.valor = valor[-1]
        conta_consumo.periodo_referencia = self.get_data(text, 'Periodo de faturacao:', '\r\n')

        # WARN:
        conta_consumo.data_vencimento = self.get_data(text, 'Data limite de pagamento:', 'Valor deste mes').strip()
        if not conta_consumo.data_vencimento:
            conta_consumo.data_vencimento = self.get_data(text, 'Debito a partir de', 'Valor deste mes').strip()

        # Ajusta as datas
        conta_consumo.data_emissao = self.convert_2_default_date(conta_consumo.data_emissao, 'DMY')
        conta_consumo.data_vencimento = self.convert_2_default_date(conta_consumo.data_vencimento, 'DMY', full_month=True)

        return self.adjust_data(conta_consumo)

        
        
        

        




