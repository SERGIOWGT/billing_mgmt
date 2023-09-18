import io
import os
from dataclasses import dataclass
from datetime import datetime
from typing import Any, List
from openpyxl import load_workbook
import pandas as pd
from src.domain.entities.response_error import UtilityBillIgnoredResponse, UtilityBillDuplicatedResponse, UtilityBillOkResponse, UtilityBillErrorResponse
from src.domain.enums import ServiceProviderEnum, ServiceTypeEnum, DocumentTypeEnum
from src.infra.handlers.google_drive_handler import GoogleDriveHandler


@dataclass
class ResultsSaver:
    _log: Any
    _drive: GoogleDriveHandler

    def __init__(self, log, drive: GoogleDriveHandler):
        self._log = log
        self._drive = drive

    def _create_df_qd28(self, list: List[UtilityBillOkResponse]) -> Any:
        def service_type_2_categoria(id_service_type):
            if id_service_type == ServiceTypeEnum.AGUA:
                return 'Água'
            if id_service_type == ServiceTypeEnum.TELECOM:
                return 'Telecomunicações'
            if id_service_type == ServiceTypeEnum.LUZ:
                return 'Eletricidade'
            return ''

        columns = ['#DATA', '#ALOJAMENTO', '#CATEGORIA', '#DESCRICAO', '#VALOR_S/IVA', '#IVA', '#VALOR_C/IVA', '#LINK']
        df = pd.DataFrame(columns=columns)
        now = datetime.now()
        for line in list:
            _dict = {}
            if line.dt_filing:
                _dict['#DATA'] = line.dt_filing.strftime("%d/%m/%Y")
            elif line.utility_bill.dt_vencimento:
                _dict['#DATA'] = line.utility_bill.dt_vencimento.strftime("%d/%m/%Y")
            else:
                _dict['#DATA'] = line.utility_bill.dt_emissao.strftime("%d/%m/%Y")
            _dict['#ALOJAMENTO'] = line.utility_bill.id_alojamento
            _dict['#CATEGORIA'] = service_type_2_categoria(line.utility_bill.tipo_servico)
            _dict['#DESCRICAO'] = line.utility_bill.periodo_referencia
            _dict['#VALOR_S/IVA'] = ''
            _dict['#IVA'] = ''
            _dict['#VALOR_C/IVA'] = str(line.utility_bill.valor).replace('.', ',')
            _dict['#LINK'] = self._drive.make_google_link(line.google_file_id)
            _dict['Arquivo Original'] = line.file_name
            _dict['Data Processamento'] = now.strftime("%Y/%m/%d.%H:%M:%S")

            df = pd.concat([df, pd.DataFrame.from_records([_dict])])
        return df


    def _create_df_ok(self, list: List[UtilityBillOkResponse]) -> Any:
        columns = ['QQ Destino', 'Alojamento', 'Ano Emissao', 'Mes Emissao', 'Concessionaria', 'Tipo Servico', 'Tipo Documento', 'N. Contrato', 'N. Cliente', 'N. Contribuinte',
                   'Local Consumo', 'Instalacao', 'N. Documento / N. Fatura', 'Periodo Referencia', 'Inicio Referencia', 'Fim Referencia',  'Emissao', 'Vencimento', 'Valor', 'Arquivo Google', 'Arquivo Original', 'Data Processamento']
        df = pd.DataFrame(columns=columns)
        now = datetime.now()
        for line in list:
            _dict = {}
            _dict['QQ Destino'] = 'Sim' if line.utility_bill.is_accounting else 'Não'
            _dict['Alojamento'] = line.utility_bill.id_alojamento
            _dict['Ano Emissao'] = str(line.utility_bill.dt_emissao.year)
            _dict['Mes Emissao'] = format(line.utility_bill.dt_emissao.month, '02d')
            _dict['Concessionaria'] = ServiceProviderEnum(line.utility_bill.concessionaria).name
            _dict['Tipo Servico'] = ServiceTypeEnum(line.utility_bill.tipo_servico).name
            _dict['Tipo Documento'] = DocumentTypeEnum(line.utility_bill.tipo_documento).name
            _dict['N. Contrato'] = line.utility_bill.id_contrato
            _dict['N. Cliente'] = line.utility_bill.id_cliente
            _dict['N. Contribuinte'] = line.utility_bill.id_contribuinte
            _dict['Local Consumo'] = line.utility_bill.local_consumo
            _dict['Instalacao'] = line.utility_bill.instalacao
            _dict['N. Documento / N. Fatura'] = line.utility_bill.id_documento
            _dict['Periodo Referencia'] = line.utility_bill.periodo_referencia
            _dict['Inicio Referencia'] = line.utility_bill.str_inicio_referencia
            _dict['Fim Referencia'] = line.utility_bill.str_fim_referencia
            _dict['Emissao'] = line.utility_bill.str_emissao
            _dict['Vencimento'] = line.utility_bill.str_vencimento
            _dict['Valor'] = line.utility_bill.valor
            _dict['Arquivo Google'] = self._drive.make_google_link(line.google_file_id)
            _dict['Arquivo Original'] = line.file_name
            _dict['Data Processamento'] = now.strftime("%Y/%m/%d.%H:%M:%S")

            df = pd.concat([df, pd.DataFrame.from_records([_dict])])
        return df

    def _create_df_not_found(self, list: List[UtilityBillErrorResponse]) -> Any:
        columns = ['QQ Destino', 'Concessionaria', 'Tipo Servico', 'Tipo Documento', 'N. Contrato', 'N. Cliente', 'N. Contribuinte',
                   'Local Consumo', 'Instalacao', 'N. Documento / N. Fatura', 'Periodo Referencia', 'Inicio Referencia',
                   'Fim Referencia',  'Emissao', 'Vencimento', 'Valor', 'Arquivo Google', 'Arquivo Original']

        df = pd.DataFrame(columns=columns)
        for line in list:
            _dict = {}
            _dict['QQ Destino'] = 'Sim' if line.utility_bill.is_accounting else 'Não'
            _dict['Concessionaria'] = ServiceProviderEnum(line.utility_bill.concessionaria).name
            _dict['Tipo Servico'] = ServiceTypeEnum(line.utility_bill.tipo_servico).name
            _dict['Tipo Documento'] = DocumentTypeEnum(line.utility_bill.tipo_documento).name
            _dict['N. Contrato'] = line.utility_bill.id_contrato
            _dict['N. Cliente'] = line.utility_bill.id_cliente
            _dict['N. Contribuinte'] = line.utility_bill.id_contribuinte
            _dict['Local Consumo'] = line.utility_bill.local_consumo
            _dict['Instalacao'] = line.utility_bill.instalacao
            _dict['N. Documento / N. Fatura'] = line.utility_bill.id_documento
            _dict['Periodo Referencia'] = line.utility_bill.periodo_referencia
            _dict['Inicio Referencia'] = line.utility_bill.str_inicio_referencia
            _dict['Fim Referencia'] = line.utility_bill.str_fim_referencia
            _dict['Emissao'] = line.utility_bill.str_emissao
            _dict['Vencimento'] = line.utility_bill.str_vencimento
            _dict['Valor'] = line.utility_bill.valor
            _dict['Arquivo Google'] = self._drive.make_google_link(line.google_file_id)
            _dict['Arquivo Original'] = line.file_name

            df = pd.concat([df, pd.DataFrame.from_records([_dict])])
        return df

    def _create_df_error(self, list: List[UtilityBillErrorResponse]) -> Any:
        columns = ['Concessionaria', 'Tipo Servico', 'Tipo Documento', 'N. Contrato', 'N. Cliente', 'N. Contribuinte',
                   'Local Consumo', 'Instalacao', 'N. Documento / N. Fatura', 'Periodo Referencia', 'Inicio Referencia',
                   'Fim Referencia',  'Emissao', 'Vencimento', 'Valor', 'Tipo Erro', 'Arquivo Google', 'Arquivo Original']

        df = pd.DataFrame(columns=columns)
        for line in list:
            _dict = {}
            _dict['Concessionaria'] = ServiceProviderEnum(line.utility_bill.concessionaria).name
            _dict['Tipo Servico'] = ServiceTypeEnum(line.utility_bill.tipo_servico).name
            _dict['Tipo Documento'] = DocumentTypeEnum(line.utility_bill.tipo_documento).name
            _dict['N. Contrato'] = line.utility_bill.id_contrato
            _dict['N. Cliente'] = line.utility_bill.id_cliente
            _dict['N. Contribuinte'] = line.utility_bill.id_contribuinte
            _dict['Local Consumo'] = line.utility_bill.local_consumo
            _dict['Instalacao'] = line.utility_bill.instalacao
            _dict['N. Documento / N. Fatura'] = line.utility_bill.id_documento
            _dict['Periodo Referencia'] = line.utility_bill.periodo_referencia
            _dict['Inicio Referencia'] = line.utility_bill.str_inicio_referencia
            _dict['Fim Referencia'] = line.utility_bill.str_fim_referencia
            _dict['Emissao'] = line.utility_bill.str_emissao
            _dict['Vencimento'] = line.utility_bill.str_vencimento
            _dict['Valor'] = line.utility_bill.valor
            _dict['Tipo Erro'] = line.error_type
            _dict['Arquivo Google'] = self._drive.make_google_link(line.google_file_id)
            _dict['Arquivo Original'] = line.file_name

            df = pd.concat([df, pd.DataFrame.from_records([_dict])])
        return df

    def _create_df_setup(self, list: List[UtilityBillErrorResponse]) -> Any:
        columns = ['QQ Destino', 'Alojamento', 'Concessionaria', 'Tipo Servico', 'Tipo Documento', 'N. Contrato', 'N. Cliente', 'N. Contribuinte',
                   'Local Consumo', 'Instalacao', 'N. Documento / N. Fatura', 'Periodo Referencia', 'Inicio Referencia',
                   'Fim Referencia',  'Emissao', 'Vencimento', 'Valor', 'Tipo Erro', 'Arquivo Google', 'Arquivo Original']

        df = pd.DataFrame(columns=columns)
        for line in list:
            _dict = {}
            _dict['QQ Destino'] = 'Sim' if line.utility_bill.is_accounting else 'Não'
            _dict['Alojamento'] = line.utility_bill.id_alojamento
            _dict['Concessionaria'] = ServiceProviderEnum(line.utility_bill.concessionaria).name
            _dict['Tipo Servico'] = ServiceTypeEnum(line.utility_bill.tipo_servico).name
            _dict['Tipo Documento'] = DocumentTypeEnum(line.utility_bill.tipo_documento).name
            _dict['N. Contrato'] = line.utility_bill.id_contrato
            _dict['N. Cliente'] = line.utility_bill.id_cliente
            _dict['N. Contribuinte'] = line.utility_bill.id_contribuinte
            _dict['Local Consumo'] = line.utility_bill.local_consumo
            _dict['Instalacao'] = line.utility_bill.instalacao
            _dict['N. Documento / N. Fatura'] = line.utility_bill.id_documento
            _dict['Periodo Referencia'] = line.utility_bill.periodo_referencia
            _dict['Inicio Referencia'] = line.utility_bill.str_inicio_referencia
            _dict['Fim Referencia'] = line.utility_bill.str_fim_referencia
            _dict['Emissao'] = line.utility_bill.str_emissao
            _dict['Vencimento'] = line.utility_bill.str_vencimento
            _dict['Valor'] = line.utility_bill.valor
            _dict['Tipo Erro'] = line.error_type
            _dict['Arquivo Google'] = self._drive.make_google_link(line.google_file_id)
            _dict['Arquivo Original'] = line.file_name

            df = pd.concat([df, pd.DataFrame.from_records([_dict])])
        return df


    def _create_df_duplicated(self, list: List[UtilityBillDuplicatedResponse]) -> Any:
        columns = ['Alojamento', 'Ano Emissao', 'Mes Emissao', 'Concessionaria', 'Tipo Servico', 'Tipo Documento', 'N. Contrato', 'N. Cliente', 'N. Contribuinte',
                   'Local Consumo', 'Instalacao', 'N. Documento / N. Fatura', 'Periodo Referencia', 'Inicio Referencia',
                   'Fim Referencia',  'Emissao', 'Vencimento', 'Valor', 'Tipo', 'Arquivo Google', 'Arquivo Pago', 'Arquivo Original']

        df = pd.DataFrame(columns=columns)
        for line in list:
            _dict = {}
            _dict['Alojamento'] = line.utility_bill.id_alojamento
            _dict['Ano Emissao'] = str(line.utility_bill.dt_emissao.year)
            _dict['Mes Emissao'] = format(line.utility_bill.dt_emissao.month, '02d')
            _dict['Concessionaria'] = ServiceProviderEnum(line.utility_bill.concessionaria).name
            _dict['Tipo Servico'] = ServiceTypeEnum(line.utility_bill.tipo_servico).name
            _dict['Tipo Documento'] = DocumentTypeEnum(line.utility_bill.tipo_documento).name
            _dict['N. Contrato'] = line.utility_bill.id_contrato
            _dict['N. Cliente'] = line.utility_bill.id_cliente
            _dict['N. Contribuinte'] = line.utility_bill.id_contribuinte
            _dict['Local Consumo'] = line.utility_bill.local_consumo
            _dict['Instalacao'] = line.utility_bill.instalacao
            _dict['N. Documento / N. Fatura'] = line.utility_bill.id_documento
            _dict['Periodo Referencia'] = line.utility_bill.periodo_referencia
            _dict['Inicio Referencia'] = line.utility_bill.str_inicio_referencia
            _dict['Fim Referencia'] = line.utility_bill.str_fim_referencia
            _dict['Emissao'] = line.utility_bill.str_emissao
            _dict['Vencimento'] = line.utility_bill.str_vencimento
            _dict['Valor'] = line.utility_bill.valor
            _dict['Tipo'] = line.error_type
            _dict['Arquivo Google'] = self._drive.make_google_link(line.google_file_id)
            _dict['Arquivo Pago'] = line.original_google_link
            _dict['Arquivo Original'] = line.file_name

            df = pd.concat([df, pd.DataFrame.from_records([_dict])])
        return df


    def _create_df_expired(self, list: List[UtilityBillDuplicatedResponse]) -> Any:
        columns = ['Alojamento', 'Ano Emissao', 'Mes Emissao', 'Concessionaria', 'Tipo Servico', 'Tipo Documento', 'N. Contrato', 'N. Cliente', 'N. Contribuinte',
                 'Local Consumo', 'Instalacao', 'N. Documento / N. Fatura', 'Periodo Referencia', 'Inicio Referencia',
                 'Fim Referencia',  'Emissao', 'Vencimento', 'Valor', 'Tipo', 'Arquivo Google', 'Arquivo Original']

        df = pd.DataFrame(columns=columns)
        for line in list:
            _dict = {}
            _dict['Alojamento'] = line.utility_bill.id_alojamento
            _dict['Ano Emissao'] = str(line.utility_bill.dt_emissao.year)
            _dict['Mes Emissao'] = format(line.utility_bill.dt_emissao.month, '02d')
            _dict['Concessionaria'] = ServiceProviderEnum(line.utility_bill.concessionaria).name
            _dict['Tipo Servico'] = ServiceTypeEnum(line.utility_bill.tipo_servico).name
            _dict['Tipo Documento'] = DocumentTypeEnum(line.utility_bill.tipo_documento).name
            _dict['N. Contrato'] = line.utility_bill.id_contrato
            _dict['N. Cliente'] = line.utility_bill.id_cliente
            _dict['N. Contribuinte'] = line.utility_bill.id_contribuinte
            _dict['Local Consumo'] = line.utility_bill.local_consumo
            _dict['Instalacao'] = line.utility_bill.instalacao
            _dict['N. Documento / N. Fatura'] = line.utility_bill.id_documento
            _dict['Periodo Referencia'] = line.utility_bill.periodo_referencia
            _dict['Inicio Referencia'] = line.utility_bill.str_inicio_referencia
            _dict['Fim Referencia'] = line.utility_bill.str_fim_referencia
            _dict['Emissao'] = line.utility_bill.str_emissao
            _dict['Vencimento'] = line.utility_bill.str_vencimento
            _dict['Valor'] = line.utility_bill.valor
            _dict['Tipo'] = line.error_type
            _dict['Arquivo Google'] = self._drive.make_google_link(line.google_file_id)
            _dict['Arquivo Original'] = line.file_name

            df = pd.concat([df, pd.DataFrame.from_records([_dict])])
        return df


    def _create_df_ignored(self, list: List[UtilityBillIgnoredResponse]) -> Any:
        columns = ['Tipo Erro', 'Arquivo Google', 'Arquivo Original']
        df = pd.DataFrame(columns=columns)
        for line in list:
            _dict = {}
            _dict['Tipo Erro'] = line.error_type
            _dict['Arquivo Google'] = self._drive.make_google_link(line.google_file_id)
            _dict['Arquivo Original'] = line.file_name
            df = pd.concat([df, pd.DataFrame.from_records([_dict])])
        return df

    def execute(self, exports_file_path: str, qd28_file_path: str, database_file_path: str, all_lists: dict, payments_file_id: str):
        ok_list = all_lists['processed_list']
        not_found_list = all_lists['not_found_list']
        error_list = all_lists['error_list']
        expired_list = all_lists['expired_list']
        duplicate_list = all_lists['duplicate_list']
        ignored_list = all_lists['ignored_list']
        setup_list = all_lists['setup_list']

        ok_list.sort(key=lambda x: x.utility_bill.concessionaria)
        not_found_list.sort(key=lambda x: x.utility_bill.concessionaria)
        duplicate_list.sort(key=lambda x: x.utility_bill.concessionaria)
        error_list.sort(key=lambda x: x.utility_bill.concessionaria)

        df_ok = self._create_df_ok(ok_list)
        df_nf = self._create_df_not_found(not_found_list)
        df_error = self._create_df_error(error_list)
        df_expired = self._create_df_expired(expired_list)
        df_duplicated = self._create_df_duplicated(duplicate_list)
        df_ignored = self._create_df_ignored(ignored_list)
        df_setup = self._create_df_setup(setup_list)
        df_qd28 = self._create_df_qd28(ok_list)

        if os.path.exists(exports_file_path):
            os.remove(exports_file_path)

        with pd.ExcelWriter(exports_file_path) as writer:
            df_ok.to_excel(writer, sheet_name='Processados', index=False)
            df_nf.to_excel(writer, sheet_name='Sem Alojamentos', index=False)
            df_error.to_excel(writer, sheet_name='Erros', index=False)
            df_expired.to_excel(writer, sheet_name='Vencidos', index=False)
            df_duplicated.to_excel(writer, sheet_name='Duplicados', index=False)
            df_setup.to_excel(writer, sheet_name='Setup', index=False)
            df_ignored.to_excel(writer, sheet_name='Ignorados', index=False)

        #if os.path.exists(qd28_file_path):
        #    os.remove(qd28_file_path)

        if (len(ok_list) > 0):
            with pd.ExcelWriter(qd28_file_path) as writer:
                df_qd28.to_excel(writer, sheet_name='Página1', index=False)

            if os.path.exists(database_file_path):
                os.remove(database_file_path)
                
            stream_file = self._drive.get_excel_file(payments_file_id)
            df_ = pd.read_excel(io.BytesIO(stream_file))

            with pd.ExcelWriter(database_file_path) as writer:
                new_df = df_.append(df_ok)
                new_df.to_excel(writer, sheet_name='Database', index=False)