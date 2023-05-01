import os
from dataclasses import dataclass
from datetime import datetime
from typing import Any, List
from openpyxl import load_workbook

import pandas as pd

from src.domain.entities.base.base_utility_bill import UtilityBillBase
from src.domain.enums import ServiceProviderEnum, ServiceTypeEnum, DocumentTypeEnum
from src.infra.google_drive_handler.Igoogle_drive_handler import \
    IGoogleDriveHandler


@dataclass
class ResultsSaver:
    _log: Any
    _drive: IGoogleDriveHandler

    def __init__(self, log, drive: IGoogleDriveHandler):
        self._log = log
        self._drive = drive

    def _create_df_ok(self, list: List[UtilityBillBase]) -> Any:
        columns = ['QQ Destino', 'Alojamento', 'Ano Emissao', 'Mes Emissao', 'Concessionaria', 'Tipo Servico', 'Tipo Documento', 'N. Contrato', 'N. Cliente', 'N. Contribuinte',
                   'Local / Instalacao', 'N. Documento / N. Fatura', 'Periodo Referencia', 'Inicio Referencia', 'Fim Referencia',  'Emissao', 'Vencimento', 'Valor', 'Diretorio Google', 'Arquivo Google', 'Link Google', 'Arquivo Original']
        df = pd.DataFrame(columns=columns)
        for line in list:
            _dict = {}
            _dict['QQ Destino'] = 'Sim' if line.is_qualquer_destino else 'Não'
            _dict['Alojamento'] = line.id_alojamento
            _dict['Ano Emissao'] = str(line.dt_emissao.year)
            _dict['Mes Emissao'] = format(line.dt_emissao.month, '02d')
            _dict['Concessionaria'] = ServiceProviderEnum(line.concessionaria).name
            _dict['Tipo Servico'] = ServiceTypeEnum(line.tipo_servico).name
            _dict['Tipo Documento'] = DocumentTypeEnum(line.tipo_documento).name
            _dict['N. Contrato'] = line.id_contrato
            _dict['N. Cliente'] = line.id_cliente
            _dict['N. Contribuinte'] = line.id_contribuinte
            _dict['Local / Instalacao'] = line.local_consumo
            _dict['N. Documento / N. Fatura'] = line.id_documento
            _dict['Periodo Referencia'] = line.periodo_referencia
            _dict['Inicio Referencia'] = line.str_inicio_referencia
            _dict['Fim Referencia'] = line.str_fim_referencia
            _dict['Emissao'] = line.str_emissao
            _dict['Vencimento'] = line.str_vencimento
            _dict['Valor'] = line.valor
            _dict['Diretorio Google'] = line.diretorio_google
            _dict['Arquivo Google'] = line.nome_arquivo_google
            _dict['Link Google'] = line.link_google
            _dict['Arquivo Original'] = line.file_name

            df = pd.concat([df, pd.DataFrame.from_records([_dict])])
        return df

    def _create_df_sem_Accommodation(self, list: List[UtilityBillBase]) -> Any:
        columns = ['QQ Destino', 'Concessionaria', 'Tipo Servico', 'Tipo Documento', 'N. Contrato', 'N. Cliente', 'N. Contribuinte',
                   'Local / Instalacao', 'N. Documento / N. Fatura', 'Periodo Referencia', 'Inicio Referencia',
                   'Fim Referencia',  'Emissao', 'Vencimento', 'Valor', 'Link Google', 'Arquivo Original']

        df = pd.DataFrame(columns=columns)
        for line in list:
            _dict = {}
            _dict['QQ Destino'] = 'Sim' if line.is_qualquer_destino else 'Não'
            _dict['Concessionaria'] = ServiceProviderEnum(line.concessionaria).name
            _dict['Tipo Servico'] = ServiceTypeEnum(line.tipo_servico).name
            _dict['Tipo Documento'] = DocumentTypeEnum(line.tipo_documento).name
            _dict['N. Contrato'] = line.id_contrato
            _dict['N. Cliente'] = line.id_cliente
            _dict['N. Contribuinte'] = line.id_contribuinte
            _dict['Local / Instalacao'] = line.local_consumo
            _dict['N. Documento / N. Fatura'] = line.id_documento
            _dict['Periodo Referencia'] = line.periodo_referencia
            _dict['Inicio Referencia'] = line.str_inicio_referencia
            _dict['Fim Referencia'] = line.str_fim_referencia
            _dict['Emissao'] = line.str_emissao
            _dict['Vencimento'] = line.str_vencimento
            _dict['Valor'] = line.valor
            _dict['Link Google'] = line.link_google
            _dict['Arquivo Original'] = line.file_name

            df = pd.concat([df, pd.DataFrame.from_records([_dict])])
        return df

    def _create_df_error(self, list: List[UtilityBillBase]) -> Any:
        columns = ['QQ Destino', 'Concessionaria', 'Tipo Servico', 'Tipo Documento', 'N. Contrato', 'N. Cliente', 'N. Contribuinte',
                   'Local / Instalacao', 'N. Documento / N. Fatura', 'Periodo Referencia', 'Inicio Referencia',
                   'Fim Referencia',  'Emissao', 'Vencimento', 'Valor', 'Erro', 'Link Google', 'Arquivo Original']

        df = pd.DataFrame(columns=columns)
        for line in list:
            _dict = {}
            _dict['QQ Destino'] = 'Sim' if line.is_qualquer_destino else 'Não'
            _dict['Concessionaria'] = ServiceProviderEnum(line.concessionaria).name
            _dict['Tipo Servico'] = ServiceTypeEnum(line.tipo_servico).name
            _dict['Tipo Documento'] = DocumentTypeEnum(line.tipo_documento).name
            _dict['N. Contrato'] = line.id_contrato
            _dict['N. Cliente'] = line.id_cliente
            _dict['N. Contribuinte'] = line.id_contribuinte
            _dict['Local / Instalacao'] = line.local_consumo
            _dict['N. Documento / N. Fatura'] = line.id_documento
            _dict['Periodo Referencia'] = line.periodo_referencia
            _dict['Inicio Referencia'] = line.str_inicio_referencia
            _dict['Fim Referencia'] = line.str_fim_referencia
            _dict['Emissao'] = line.str_emissao
            _dict['Vencimento'] = line.str_vencimento
            _dict['Valor'] = line.valor
            _dict['Erro'] = line.str_erro
            _dict['Link Google'] = line.link_google
            _dict['Arquivo Original'] = line.file_name

            df = pd.concat([df, pd.DataFrame.from_records([_dict])])
        return df

    def _create_df_ignored(self, list) -> Any:
        columns = ['Erro', 'Link Google', 'Arquivo']
        df = pd.DataFrame(columns=columns)
        for line in list:
            _dict = {}
            _dict['Erro'] = line['msg']
            _dict['Link Google'] = line['Link Google']
            _dict['Arquivo'] = line['file_name']
            df = pd.concat([df, pd.DataFrame.from_records([_dict])])
        return df

    def execute(self, database_folder: str, export_folder: str, new_ok_list: List[UtilityBillBase], not_found_list: List[UtilityBillBase], error_list: List[UtilityBillBase], ignored_list: List[Any], count_contas_pagas: int):
        new_ok_list.sort(key=lambda x: x.concessionaria)
        not_found_list.sort(key=lambda x: x.concessionaria)
        error_list.sort(key=lambda x: x.concessionaria)

        df_ok = self._create_df_ok(new_ok_list)
        df_nf = self._create_df_sem_Accommodation(not_found_list)
        df_error = self._create_df_error(error_list)
        df_ignored = self._create_df_ignored(ignored_list)

        now = datetime.now()
        output_file_name = f'output_{now.strftime("%Y-%m-%d.%H.%M.%S")}.xlsx'
        output_file_name = os.path.join(export_folder, output_file_name)
        with pd.ExcelWriter(output_file_name) as writer:
            df_ok.to_excel(writer, sheet_name='Processados', index=False)
            df_nf.to_excel(writer, sheet_name='Sem Alojamentos', index=False)
            df_error.to_excel(writer, sheet_name='Erros', index=False)
            df_ignored.to_excel(writer, sheet_name='Ignorados', index=False)

        output_file_name = 'database.xlsx'
        output_file_name = os.path.join(database_folder, output_file_name)
        if os.path.exists(output_file_name) is False:
            with pd.ExcelWriter(output_file_name) as writer:
                df_ok.to_excel(writer, sheet_name='Database', index=False)
        else:
            if len(new_ok_list) > 0:
                book = load_workbook(output_file_name)
                with pd.ExcelWriter(output_file_name) as writer:
                    writer.book = book
                    ws = writer.sheets['Database']

                    # adiciona o dataframe na planilha excel
                    for row in df_ok.iterrows():
                        ws.append(row[1].tolist())
                        
                    # salva as alterações no arquivo Excel
                    writer.save()
            
        return
        
