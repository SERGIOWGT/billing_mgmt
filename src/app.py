import copy
import io
import os
from dataclasses import dataclass
import re
from typing import List
import pandas as pd
from src.domain.entities.base.base_utility_bill import UtilityBillBase
from src.domain.entities.paid_utility_bill import PaidUtilityBill
from src.domain.entities.paid_utility_bill_list import PaidUtilityBillList
from src.services.results_saver import ResultsSaver

from src.infra.google_drive_handler.Igoogle_drive_handler import IGoogleDriveHandler
from src.domain.enums.service_provider_enum import ServiceProviderEnum
from src.domain.entities.accommodation import Accommodation
from src.domain.entities.accommodation_list import AccommodationList
from src.services.files_handler import FilesHandler
from src.infra.email_handler.Imail_handler import IEmailHandler
from src.infra.email_handler.email_handler import EmailHandler
from src.services.attachment_downloader import AttachmentDownloader
from src.services.results_uploader import ResultsUploader

from src.infra.exception_handler import ApplicationException


@dataclass
class App:
    def __init__(self, accommodation_file_id: str, drive: IGoogleDriveHandler, log):
        ApplicationException.when(log is None, 'Log não iniciado.')
        ApplicationException.when(drive is None, 'Google Drive não iniciado.', log)
        ApplicationException.when(accommodation_file_id == '', 'Chave "accommodation_file_id" não encontrada no arquivo de configuração.', log)
        self._accommodation_file_id = accommodation_file_id
        self._drive = drive
        self._log = log
        self._dict_config = {}

    def _get_processed_utility_bills(self, base_folder) -> PaidUtilityBillList:
        file_name = os.path.join(base_folder, 'database', 'database.xlsx')
        if os.path.exists(file_name) is False:
            return PaidUtilityBillList([])

        contas = []
        df_ = pd.read_excel(file_name, dtype={'N. Documento / N. Fatura': object})
        df = df_.where(pd.notnull(df_), None)
        cols = df.shape[1]
        ApplicationException.when(cols != 22, 'A Planilha de Histórico deve ter 22 colunas. ', self._log)
        expected_columns = ['QQ Destino', 'Alojamento', 'Ano Emissao', 'Mes Emissao', 'Concessionaria', 'Tipo Servico', 'Tipo Documento', 'N. Contrato', 'N. Cliente', 'N. Contribuinte', 'Local / Instalacao',
                            'N. Documento / N. Fatura', 'Periodo Referencia', 'Inicio Referencia', 'Fim Referencia', 'Emissao', 'Vencimento', 'Valor', 'Diretorio Google', 'Arquivo Google', 'Link Google', 'Arquivo Original']
        actual_columns = df.columns.tolist()

        ApplicationException.when(expected_columns != actual_columns, f'A Planilha Histórica deveria ter as colunas {actual_columns}.', self._log)
        for _, row in df.iterrows():
            nome_concessionaria = row['Concessionaria']
            nome_concessionaria = nome_concessionaria.replace('\n', '')
            nome_tipo_servico = row['Tipo Servico']
            nome_tipo_servico = nome_tipo_servico.replace('\n', '')
            nome_Accommodation = row['Alojamento']
            id_documento = row['N. Documento / N. Fatura']
            dt_emissao = row['Emissao']
            contas.append(PaidUtilityBill(nome_concessionaria, nome_tipo_servico, nome_Accommodation, id_documento, dt_emissao))

        return PaidUtilityBillList(contas)

    def _get_allowed_senders(self) -> List[str]:
        sheet_name = 'Senders'
        stream_file = self._drive.get_excel_file(self._accommodation_file_id)
        df_ = pd.read_excel(io.BytesIO(stream_file), sheet_name=sheet_name)
        df = df_.where(pd.notnull(df_), None)
        cols = df.shape[1]
        ApplicationException.when(cols != 2, f'A Sheet "{sheet_name}" da planilha de Alojamentoss deve ter 2 colunas. ', self._log)
        expected_columns = ['Email', 'Habilitado']
        actual_columns = df.columns.tolist()
        ApplicationException.when(expected_columns != actual_columns, f'A sheet "{sheet_name}" da planilha de Alojamentoss deveria ter as colunas {actual_columns}.', self._log)

        senders = []
        for _, row in df.iterrows():
            senders.append(row['Email'])

        return senders

    def _get_accommodations(self) -> AccommodationList:
        def remove_space_and_dot(value: str) -> str:
            return re.sub('[.\s]+', '', value)
            
        sheet_name = 'Alojamentos'
        stream_file = self._drive.get_excel_file(self._accommodation_file_id)
        df_ = pd.read_excel(io.BytesIO(stream_file), sheet_name=sheet_name)
        df = df_.where(pd.notnull(df_), None)
        cols = df.shape[1]
        ApplicationException.when(cols != 19, f'A Sheet "{sheet_name}" da planilha de Alojamentos deve ter 19 colunas. ', self._log)

        Accommodations = []
        for _, row in df.iterrows():
            column_list = row.index.tolist()
                        
            nome_alojamento = row['Alojamento']
            diretorio = row['Google Drive']
            nif = row['NIF Titular']
            for id_concessionaria in [x for x in list(ServiceProviderEnum) if x != ServiceProviderEnum.DESCONHECIDO]:
                nome_concessionaria = str(id_concessionaria).replace('ServiceProviderEnum.', '')
                nome_concessionaria = nome_concessionaria.replace(' ', '')

                conta = row[f'{nome_concessionaria} Contrato'] if f'{nome_concessionaria} Contrato' in column_list else ''
                cliente = row[f'{nome_concessionaria} Cliente'] if f'{nome_concessionaria} Cliente' in column_list else ''
                local = row[f'{nome_concessionaria} Local Consumo'] if f'{nome_concessionaria} Local Consumo' in column_list else ''

                cliente = '' if (str(cliente) == 'None') else remove_space_and_dot(cliente)
                conta = '' if (str(conta) == 'None') else remove_space_and_dot(conta)
                local = '' if (str(local) == 'None') else remove_space_and_dot(local)
                nome_alojamento = '' if (str(nome_alojamento) == 'None') else str(nome_alojamento).replace(' ', '')
                diretorio = '' if (str(diretorio) == 'None') else str(diretorio).replace(' ', '')

                if cliente or conta or local:
                    Accommodations.append(Accommodation(id_concessionaria, nome_alojamento, diretorio, nif, cliente, conta, local))

        return AccommodationList(Accommodations)

    def _get_config_key(self, key: str) -> str:
        value = self._dict_config.get(key, '')
        ApplicationException.when(value == '', f'Chave não encontrada no arquivo de Accommodations. [key={key}]', self._log)
        return value

    def _get_email_handler(self) -> IEmailHandler:
        email = EmailHandler()
        smtp_server = self._get_config_key('gmail.imap.server')
        user = self._get_config_key('gmail.user')
        password = self._get_config_key('gmail.password')

        try:
            email.login(smtp_server, user, password, use_ssl=True)
        except Exception as error:
            msg = str(error)
            self._log.critical(msg)
            raise ApplicationException('Erro ao conectar nom email') from error

        return email

    def _download_emails(self, email: IEmailHandler, download_folder: str) -> None:
        input_email_folder = self._get_config_key('gmail.reading.folder')
        output_email_folder = self._get_config_key('gmail.output.folder')
        self._log.info('Baixando os remetentes permitidos na planilha de Alojamentoss')
        senders = self._get_allowed_senders()
        self._log.info('Baixando os arquivos anexados')
        AttachmentDownloader.execute(download_folder, input_email_folder, output_email_folder, senders, self._log, email)

    def _clean_directories(self, download_folder: str, ok_list: List[UtilityBillBase], ignored_list: List[dict]):
        destination_folder = os.path.join(download_folder, 'processados')
        list_2_move = [conta.file_name for conta in ok_list]
        FilesHandler.move_files(self._log, destination_folder, list_2_move)

        destination_folder = os.path.join(download_folder, 'ignorados')
        list_2_move = [conta['file_name'] for conta in ignored_list]
        FilesHandler.move_files(self._log, destination_folder, list_2_move)

    def _handle_downloaded_files(self, download_folder: str, processed_utility_bills) -> None:
        self._log.info('Baixando os alojamentos da planilha de Alojamentos')
        accommodations = self._get_accommodations()
        self._log.info('Analisando os arquivo')
        return FilesHandler.execute(self._log, download_folder, accommodations, processed_utility_bills)

    def _process_exceptions(self, processed_list: List[UtilityBillBase]) -> None:
        self._excecoes(processed_list)

    def _upload_files(self, folder_base_id, others_folder_base_id, folder_contabil_id, processed_list, not_found_list, error_list, ignored_list) -> None:
        uploader = ResultsUploader(self._log, self._drive)

        self._log.info('Uploading lista de contas processadas')
        # uploader.upload_ok_list(folder_base_id, folder_contabil_id, processed_list)
        self._log.info(f'{len(processed_list)} arquivo(s) processados')

        self._log.info('Uploading lista de contas nao processadas')
        # uploader.upload_other_list(others_folder_base_id, not_found_list, error_list, ignored_list)
        self._log.info(f'{len(not_found_list)} arquivo(s) sem Alojamentos')
        self._log.info(f'{len(error_list)} arquivo(s) com erro')
        self._log.info(f'{len(ignored_list)} arquivo(s) ignorados')

    def _export_results(self, export_folder: str, database_folder: str, processed_list, not_found_list, error_list, ignored_list, processed_utility_bills: PaidUtilityBillList):
        saver = ResultsSaver(self._log, self._drive)
        saver.execute(database_folder, export_folder, processed_list, not_found_list, error_list, ignored_list, processed_utility_bills.count+1)

    def _handle_exceptions(self, ok_list: List[UtilityBillBase]) -> None:
        excp1 = [conta for conta in ok_list if conta.id_cliente == '1424424667' and conta.id_contrato == '1424424664' and conta.concessionaria == ServiceProviderEnum.ALTICE_MEO]
        if len(excp1) > 0:
            for conta in excp1:
                new_conta = copy.deepcopy(conta)
                new_conta.id_alojamento = 'BD_Fernandes108_3' if conta.id_alojamento == 'BD_Fernandes108_4' else 'BD_Fernandes108_4'

                valor_original = conta.valor
                parcela1 = round(valor_original / 2, 2)
                parcela2 = valor_original - parcela1
                conta.valor = parcela1
                new_conta.valor = parcela2

                ok_list.append(new_conta)

    def _get_config_infos_from_accommodation_file(self) -> dict:
        sheet_name = 'Config'
        stream_file = self._drive.get_excel_file(self._accommodation_file_id)
        df_ = pd.read_excel(io.BytesIO(stream_file), sheet_name=sheet_name)
        df = df_.where(pd.notnull(df_), None)
        cols = df.shape[1]
        ApplicationException.when(cols != 3, f'A Sheet "{sheet_name}" da planilha de Alojamentoss deve ter 3 colunas. ', self._log)
        expected_columns = ['Name', 'Value', 'Explanation']
        actual_columns = df.columns.tolist()
        ApplicationException.when(expected_columns != actual_columns, f'A sheet "{sheet_name}" da planilha de Alojamentoss deveria ter as seguintes colunas {actual_columns}.', self._log)
        dict = {}
        for _, row in df.iterrows():
            dict[row['Name']] = row['Value']
        return dict

    def _validate_required_settings(self) -> None:
        _ = self._get_config_key('localbase.folder')
        _ = self._get_config_key('gmail.imap.server')
        _ = self._get_config_key('gmail.user')
        _ = self._get_config_key('gmail.password')
        _ = self._get_config_key('gmail.reading.folder')
        _ = self._get_config_key('gmail.output.folder')
        _ = self._get_config_key('googledrive.base.folderid')
        _ = self._get_config_key('googledrive.accounting.folderid')
        _ = self._get_config_key('googledrive.otherfiles.folderid')

    def _get_download_folder(self, base_folder: str) -> str:
        folder = os.path.join(base_folder, 'downloads')
        ApplicationException.when(not os.path.exists(folder), f'Path does not exist. [{dir}]', self._log)
        return folder

    def _get_base_folder(self) -> str:
        folder = self._get_config_key('localbase.folder')
        ApplicationException.when(not os.path.exists(folder), f'Path does not exist. [{dir}]', self._log)
        return folder

    def execute(self):
        self._log.info('Inicio da rotina App.execute')
        self._log.info('Pegando as configurações da planilha de Alojamentoss')
        self._dict_config = self._get_config_infos_from_accommodation_file()
        self._log.info('Checando as configurações')
        self._validate_required_settings()
        base_folder = self._get_base_folder()
        download_folder = self._get_download_folder(base_folder)
        self._log.info(f'Folders: {base_folder}{download_folder}')
        self._log.info('Baixando as contas pagas da planilha historica')
        processed_utility_bills = self._get_processed_utility_bills(base_folder)

        base_folder = self._get_base_folder()
        download_folder = self._get_download_folder(base_folder)
        self._log.info(f'Folders: {base_folder}{download_folder}')

        self._log.info('Conectando Email...')
        email = self._get_email_handler()
        self._log.info('Baixando os PDFS dos email')
        self._download_emails(email, download_folder)

        self._log.info('Analisando os arquivos do diretorio de downloads')
        processed_list, not_found_list, error_list, ignored_list = self._handle_downloaded_files(download_folder, processed_utility_bills)
        self._log.info('Processando as excecoes')
        self._handle_exceptions(processed_list)

        folder_base_id = self._get_config_key('googledrive.base.folderid')
        folder_contabil_id = self._get_config_key('googledrive.accounting.folderid')
        others_folder_base_id = self._get_config_key('googledrive.otherfiles.folderid')
        self._upload_files(folder_base_id, others_folder_base_id, folder_contabil_id, processed_list, not_found_list, error_list, ignored_list)

        export_folder = os.path.join(base_folder, 'exports')
        database_folder = os.path.join(base_folder, 'database')
        self._log.info('Salvando as planilhas')
        self._export_results(export_folder, database_folder, processed_list, not_found_list, error_list, ignored_list, processed_utility_bills)

        self._log.info('Limpando o diretorio de downloads')
        self._clean_directories(download_folder, processed_list, ignored_list)
        email.logout()
