import copy
import io
import os
from dataclasses import dataclass
import re
from typing import List
import pandas as pd

from src.domain.entities.response_error import UtilityBillIgnoredResponse, UtilityBillDuplicatedResponse, UtilityBillOkResponse, UtilityBillErrorResponse
from src.domain.entities.base.base_utility_bill import UtilityBillBase
from src.domain.entities.paid_utility_bill import PaidUtilityBill
from src.domain.entities.paid_utility_bill_list import PaidUtilityBillList
from src.services.results_saver import ResultsSaver

from src.infra.google_drive_handler.Igoogle_drive_handler import IGoogleDriveHandler
from src.domain.enums import AccommodationStatusEnum, ServiceProviderEnum, DocumentTypeEnum
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
    _folder_base_id = ''
    _folder_contabil_id = ''
    _others_folder_base_id = ''
    _export_folder = ''
    _database_folder = ''
    _download_folder = ''
    _smtp_server = ''
    _user = ''
    _password = ''
    _input_email_folder = ''
    _output_email_folder = ''
    _accommodations = ''
    _except_list = ''

    def __init__(self, accommodation_file_id: str, drive: IGoogleDriveHandler, log):
        ApplicationException.when(log is None, 'Log não iniciado.')
        ApplicationException.when(drive is None, 'Google Drive não iniciado.', log)
        ApplicationException.when(accommodation_file_id == '', 'Chave "accommodation_file_id" não encontrada no arquivo de configuração.', log)
        self._accommodation_file_id = accommodation_file_id
        self._drive = drive
        self._log = log
        self._dict_config = {}

    @classmethod
    def _remove_space_and_dot(cls, value: str) -> str:
        return re.sub('[.\s]+', '', value)

    def _get_processed_utility_bills(self) -> PaidUtilityBillList:
        self._log.info('Downloading the paid bills from the historical worksheet')
        file_name = os.path.join(self._database_folder, 'database.xlsx')
        if os.path.exists(file_name) is False:
            return PaidUtilityBillList([])

        contas = []
        df_ = pd.read_excel(file_name, dtype={'N. Documento / N. Fatura': object})
        df = df_.where(pd.notnull(df_), None)
        cols = df.shape[1]
        ApplicationException.when(cols != 22, 'History Sheet must have 22 columns. ', self._log)
        expected_columns = ['QQ Destino', 'Alojamento', 'Ano Emissao', 'Mes Emissao', 'Concessionaria', 'Tipo Servico',
                            'Tipo Documento', 'N. Contrato', 'N. Cliente', 'N. Contribuinte', 'Local / Instalacao',
                            'N. Documento / N. Fatura', 'Periodo Referencia', 'Inicio Referencia', 'Fim Referencia', 
                            'Emissao', 'Vencimento', 'Valor', 'Diretorio Google', 'Arquivo Google', 'Arquivo Original', 'Data Processamento']
        actual_columns = df.columns.tolist()

        ApplicationException.when(expected_columns != actual_columns, f'The Historical Spreadsheet should have the columns {actual_columns}.', self._log)
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

    def _get_accommodations(self) -> AccommodationList:
        sheet_name = 'Alojamentos'
        stream_file = self._drive.get_excel_file(self._accommodation_file_id)
        df_ = pd.read_excel(io.BytesIO(stream_file), sheet_name=sheet_name)
        df = df_.where(pd.notnull(df_), None)
        cols = df.shape[1]
        ApplicationException.when(cols != 20, f'A Sheet "{sheet_name}" da planilha de Alojamentos deve ter 20 colunas. ', self._log)

        accommodation_status_list = list(AccommodationStatusEnum)

        list_aux = []
        for _, row in df.iterrows():
            column_list = row.index.tolist()

            nome_alojamento = row['Alojamento']
            diretorio = row['Google Drive']
            nif = row['NIF Titular']
            status = row['Status']
            ApplicationException.when(status not in accommodation_status_list, f'O alojamento "{nome_alojamento}" da planilha de Alojamentos esta com status incompativel. [{status}]', self._log)

            for id_concessionaria in [x for x in list(ServiceProviderEnum) if x != ServiceProviderEnum.DESCONHECIDO]:
                nome_concessionaria = str(id_concessionaria).replace('ServiceProviderEnum.', '')
                nome_concessionaria = nome_concessionaria.replace(' ', '')

                conta = row[f'{nome_concessionaria} Contrato'] if f'{nome_concessionaria} Contrato' in column_list else ''
                cliente = row[f'{nome_concessionaria} Cliente'] if f'{nome_concessionaria} Cliente' in column_list else ''
                local = row[f'{nome_concessionaria} Local Consumo'] if f'{nome_concessionaria} Local Consumo' in column_list else ''

                cliente = '' if (str(cliente) == 'None') else self._remove_space_and_dot(cliente)
                conta = '' if (str(conta) == 'None') else self._remove_space_and_dot(conta)
                local = '' if (str(local) == 'None') else self._remove_space_and_dot(local)
                nome_alojamento = '' if (str(nome_alojamento) == 'None') else str(nome_alojamento).replace(' ', '')
                diretorio = '' if (str(diretorio) == 'None') else str(diretorio).replace(' ', '')

                if cliente or conta or local:
                    list_aux.append(Accommodation(id_concessionaria, status, nome_alojamento, diretorio, nif, cliente, conta, local))

        self._accommodations = AccommodationList(list_aux)

    def _get_except_list(self) -> None:
        sheet_name = 'Excecoes'
        stream_file = self._drive.get_excel_file(self._accommodation_file_id)
        df_ = pd.read_excel(io.BytesIO(stream_file), sheet_name=sheet_name)
        df = df_.where(pd.notnull(df_), None)
        cols = df.shape[1]
        ApplicationException.when(cols != 4, f'A Sheet "{sheet_name}" da planilha de Alojamentos deve ter 4 colunas. ', self._log)
        expected_columns = ['Alojamento Origem', 'Concessionaria', 'Tipo de Excecao', 'Alojamentos Destino']
        actual_columns = df.columns.tolist()
        ApplicationException.when(expected_columns != actual_columns, f'A sheet "{sheet_name}" da planilha de Alojamentoss deveria ter as seguintes colunas {actual_columns}.', self._log)

        result = {}
        for _, row in df.iterrows():
            accommodation_name_in = row['Alojamento Origem']
            except_type  = row['Tipo de Excecao']
            nome_concessionaria = row['Concessionaria']
            accommodations_name_out = row['Alojamentos Destino']
            vet_accommodations = accommodations_name_out.split(';')
            ApplicationException.when(len(vet_accommodations) == 0, f'O alojamento "{accommodation_name_in}" esta com registro de exceção incompativel. [{accommodations_name_out}]', self._log)
            for index in range(len(vet_accommodations)):
                vet_accommodations[index] = vet_accommodations[index].strip()
                ApplicationException.when(
                    any(x for x in self._accommodations.Accommodations if x.nome == vet_accommodations[index]) is False,
                    f'O alojamento "{accommodation_name_in}" esta com registro de exceção incompativel. [{accommodations_name_out}]', self._log)

            result[(accommodation_name_in, nome_concessionaria)] = (except_type, vet_accommodations)

        self._except_list = result

    def _get_config_key(self, key: str) -> str:
        value = self._dict_config.get(key, '')
        ApplicationException.when(value == '', f'Chave não encontrada no arquivo de Accommodations. [key={key}]', self._log)
        return value

    def _get_email_handler(self) -> IEmailHandler:
        self._log.info('Connecting Email...')
        email = EmailHandler()

        try:
            email.login(self._smtp_server, self._user, self._password, use_ssl=True)
        except Exception as error:
            msg = str(error)
            self._log.critical(msg)
            raise ApplicationException('Error connecting email') from error

        return email

    def _download_emails(self, email: IEmailHandler) -> None:
        self._log.info('Downloading PDF files from emails')
        AttachmentDownloader.execute(self._download_folder, self._input_email_folder, self._output_email_folder, self._log, email)

    def _clean_directories(self, ok_list: List[UtilityBillBase], ignored_list: List[UtilityBillIgnoredResponse]):
        self._log.info('Cleaning up directories')
        destination_folder = os.path.join(self._download_folder, 'processados')
        list_2_move = [conta.complete_file_name for conta in ok_list]
        FilesHandler.move_files(self._log, destination_folder, list_2_move)

        destination_folder = os.path.join(self._download_folder, 'ignorados')
        list_2_move = [conta.complete_file_name for conta in ignored_list]
        FilesHandler.move_files(self._log, destination_folder, list_2_move)

    def _handle_downloaded_files(self, processed_utility_bills) -> None:
        self._log.info('Processing downloaded files')
        return FilesHandler.execute(self._log, self._download_folder, self._accommodations, processed_utility_bills)

    def _process_exceptions(self, processed_list: List[UtilityBillBase]) -> None:
        self._log.info('Processing the exceptions')
        if len(processed_list) == 0:
            return

        if len(self._except_list) == 0:
            return

        added_records = []
        for line in processed_list:
            conta = line.utility_bill
            exception_data = self._except_list.get((conta.id_alojamento, ServiceProviderEnum(conta.concessionaria).name), '')
            if (exception_data):
                x = self._handle_exceptions(line, exception_data)
                added_records.extend(x)

        processed_list.extend(added_records)

    def _upload_files(self, processed_list: List[UtilityBillOkResponse], not_found_list: List[UtilityBillErrorResponse], error_list: List[UtilityBillErrorResponse], duplicated_list: List[UtilityBillDuplicatedResponse], ignored_list: List[UtilityBillIgnoredResponse]) -> None:
        uploader = ResultsUploader(self._log, self._drive)

        self._log.info('Uploading list of processed')
        uploader.upload_ok_list(self._folder_base_id, self._folder_contabil_id, processed_list)
        self._log.info(f'{len(processed_list)} file(s) processed')

        self._log.info('Uploading list of unprocessed ')
        uploader.upload_other_list(self._others_folder_base_id, not_found_list, error_list, duplicated_list, ignored_list)
        self._log.info(f'{len(not_found_list)} file(s) without accommodation')
        self._log.info(f'{len(error_list)} error file(s)')
        self._log.info(f'{len(duplicated_list)} duplicate file(s)')
        self._log.info(f'{len(ignored_list)} ignored file(s)')

    def _export_results(self, processed_list, not_found_list, error_list, duplicated_list, ignored_list, processed_utility_bills: PaidUtilityBillList):
        self._log.info('Saving the worksheets')
        saver = ResultsSaver(self._log, self._drive)
        saver.execute(self._database_folder, self._export_folder, processed_list, not_found_list, error_list, duplicated_list, ignored_list, processed_utility_bills.count+1)

    def _handle_exceptions(self, line, exception_data) -> None:
        except_type = exception_data[0]
        accomm_destination_list = exception_data[1]
        parcela = round(line.utility_bill.valor / len(accomm_destination_list), 2)

        ret = []
        if except_type == 1:
            for index in range(len(accomm_destination_list)):
                new_line = copy.deepcopy(line)
                new_line.utility_bill.valor = parcela
                new_line.utility_bill.tipo_documento = DocumentTypeEnum.CONTA_CONSUMO_RATEIO
                new_line.utility_bill.id_alojamento = accomm_destination_list[index]
                ret.append(new_line)
        return ret

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

    def _get_and_validate_config(self)->None:
        def get_and_validate_folder(base_folder, folder_name) -> str:
            ret = os.path.join(base_folder, folder_name)
            ApplicationException.when(not os.path.exists(ret), f'Path does not exist. [{ret}]', self._log)
            return ret

        self._log.info('Getting the settings from the Accommodation worksheet')
        self._dict_config = self._get_config_infos_from_accommodation_file()
        self._log.info('Checking the settings')

        self._folder_base_id = self._get_config_key('googledrive.base.folderid')
        self._folder_contabil_id = self._get_config_key('googledrive.accounting.folderid')
        contabil_folder_name = self._get_config_key('googledrive.accounting.foldername')
        folder_contabil_id = self._drive.find_file(contabil_folder_name, self._folder_base_id)
        ApplicationException.when(folder_contabil_id is None, f'Accounting directory not found. [{contabil_folder_name}]', self._log)
        ApplicationException.when(folder_contabil_id != self._folder_contabil_id,
                                  f'Accounting directory found but its id must be the same as the advisor in "googledrive.accounting.folderid". [{folder_contabil_id}]', self._log)

        self._others_folder_base_id = self._get_config_key('googledrive.otherfiles.folderid')
        others_folder_name = self._get_config_key('googledrive.otherfiles.foldername')
        folder_others_id = self._drive.find_file(others_folder_name, self._folder_base_id)
        ApplicationException.when(folder_others_id is None, f'Other files directory not found [{others_folder_name}]', self._log)
        ApplicationException.when(folder_others_id != self._others_folder_base_id,
                                  f'Other files directory found but its id must be the same as the advisor in "googledrive.accounting.folderid". [{folder_others_id}]', self._log)

        base_folder = self._get_config_key('localbase.folder')
        ApplicationException.when(not os.path.exists(base_folder), f'Path does not exist. [{base_folder}]', self._log)

        self._download_folder = get_and_validate_folder(base_folder, 'downloads')
        self._export_folder = get_and_validate_folder(base_folder, 'exports')
        self._database_folder = get_and_validate_folder(base_folder, 'database')
        ApplicationException.when(not os.path.exists(self._database_folder), f'Path does not exist. [{self._database_folder}]', self._log)

        self._smtp_server = self._get_config_key('gmail.imap.server')
        self._user = self._get_config_key('gmail.user')
        self._password = self._get_config_key('gmail.password')
        self._input_email_folder = self._get_config_key('gmail.reading.folder')
        self._output_email_folder = self._get_config_key('gmail.output.folder')

        self._log.info('Downloading accommodations from the worksheet')
        self._get_accommodations()
        self._log.info('Downloading exceptions from the worksheet')
        self._get_except_list()

    def _handle_duplicates(self, processed_list: List[UtilityBillOkResponse], duplicated_list:  List[UtilityBillDuplicatedResponse]):
        index_of_duplicates = []
        for i in range(0, len(processed_list)-1):
            for j in range(i+1, len(processed_list)):
                if (processed_list[i].utility_bill == processed_list[j].utility_bill):
                    index_of_duplicates.append(j)

        for indx in sorted(index_of_duplicates, reverse=True):
            obj = processed_list[indx]
            obj.error_type = '8'
            duplicated_list.append(processed_list[indx])
            del processed_list[indx]

    def execute(self):
        self._log.info('Start of the App.execute routine')
        self._get_and_validate_config()

        processed_utility_bills = self._get_processed_utility_bills()
        email = self._get_email_handler()
        self._download_emails(email)
        processed_list, not_found_list, error_list, duplicated_list, ignored_list = self._handle_downloaded_files(processed_utility_bills)

        self._handle_duplicates(processed_list, duplicated_list)
        self._process_exceptions(processed_list)
        self._upload_files(processed_list, not_found_list, error_list, duplicated_list, ignored_list)
        self._export_results(processed_list, not_found_list, error_list, duplicated_list, ignored_list, processed_utility_bills)

        self._clean_directories(processed_list, ignored_list)
        email.logout()
