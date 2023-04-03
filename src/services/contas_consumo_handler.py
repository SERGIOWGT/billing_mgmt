import os
import pandas as pd
import io
from typing import Any, List
from dataclasses import dataclass
from src.domain.enums import ConcessionariaEnum, TipoServicoEnum
from src.domain.models.conta_consumo import ContaConsumo
from src.infra.exception_handler import ApplicationException
from src.services.conta_consumo_factory import ContaConsumoFactory
from src.infra.pdf_extractor_handler.pdf_extractor_handler import PdfExtractorHandler
from src.domain.entities.alojamentos import Alojamento, PoolAlojamentos


@dataclass
class ContaConsumoHandler:
    downloads_folder = ''
    errors_folder = ''
    processed_folder = ''

    def __init__(self, log, drive, config):
        self.config = config

        self.downloaded_folder = self.config.get('directories.downloads')
        self.processed_folder = self.downloaded_folder + '/processados'
        ApplicationException.when(not os.path.exists( self.processed_folder ), f'Path does not exist. [{ self.processed_folder }]', log)

        self.errors_folder = self.downloaded_folder + '/erros'
        ApplicationException.when(not os.path.exists( self.errors_folder ), f'Path does not exist. [{ self.errors_folder }]', log)

        self.ignored_folder = self.downloaded_folder + '/ignorados'
        ApplicationException.when(not os.path.exists( self.ignored_folder ), f'Path does not exist. [{ self.ignored_folder }]', log)

        self.export_folder = self.config.get('directories.exports')
        ApplicationException.when(not os.path.exists( self.export_folder ), f'Path does not exist. [{ self.export_folder }]', log)

        self.log = log
        self.drive = drive

    def _get_alojamentos(self) -> PoolAlojamentos:
        stream_file = self.drive.get_excel_file(self.config.get('google drive.file_accommodation_id'))
        df_ = pd.read_excel(io.BytesIO(stream_file))
        df = df_.where(pd.notnull(df_), None)

        alojamentos = []
        for index, row in df.iterrows():
            if (index < 1):
                continue 

            nome = row[2]
            diretorio = row[3]
            for empresa in [x for x in list(ConcessionariaEnum) if x != ConcessionariaEnum.NADA and x != ConcessionariaEnum.MEO]:
                cliente = row[1 + (3 * empresa)]
                conta = row[2 + (3 * empresa)]
                local = row[3 + (3 * empresa)]

                if cliente or conta or local:
                    alojamentos.append(Alojamento(empresa, nome, diretorio, str(cliente), str(conta), str(local)))

        return PoolAlojamentos(alojamentos)

    def _create_df_default(self, list: List[ContaConsumo]) -> Any:
        columns = ['Concessionaria', 'Tipo Servico', 'N. Contrato', 'N. Cliente', 'N. Contribuinte',
                   'Local / Instalacao', 'N. Documento / N. Fatura', 'Periodo Referencia', 'Emissao', 'Vencimento', 'Valor', 'Alojamento', 'Diretorio', 'Arquivo']

        df = pd.DataFrame(columns=columns)
        for line in list:
            _dict = {}
            _dict['Concessionaria'] = ConcessionariaEnum(line.concessionaria).name
            _dict['Tipo Servico'] = TipoServicoEnum(line.tipo_servico).name
            _dict['N. Contrato'] = line.id_contrato
            _dict['N. Cliente'] = line.id_cliente
            _dict['N. Contribuinte'] = line.id_contribuinte
            _dict['Local / Instalacao'] = line.local_consumo
            _dict['N. Documento / N. Fatura'] = line.id_documento
            _dict['Periodo Referencia'] = line.periodo_referencia
            _dict['Emissao'] = line.data_emissao
            _dict['Vencimento'] = line.data_vencimento
            _dict['Valor'] = line.valor
            _dict['Alojamento'] = line.id_alojamento
            _dict['Diretorio'] = line.diretorio
            _dict['Arquivo'] = line.file_name

            df = pd.concat([df, pd.DataFrame.from_records([_dict])])
        return df

    def _create_df_ignored(self, list) -> Any:
        columns = ['Erro', 'Arquivo']
        df = pd.DataFrame(columns=columns)
        for line in list:
            df = df.append({'Erro': line[0], 'Arquivo': line[1]}, ignore_index=True)

        return df

    def _result_2_excel(self, processed_list, error_list, ignored_list):
        df_ok = self._create_df_default(processed_list)
        df_error = self._create_df_default(error_list)
        df_ignored = self._create_df_ignored(ignored_list)
        output_file_name = os.path.join(self.export_folder, 'output.xlsx')

        with pd.ExcelWriter(output_file_name) as writer:
            df_ok.to_excel(writer, sheet_name='Processados', index=False)
            df_error.to_excel(writer, sheet_name='Erros', index=False)
            df_ignored.to_excel(writer, sheet_name='Ignorados', index=False)

    def _move_file(self, file_name, destination):
        try:
            os.rename(file_name, destination)
        except Exception as error:
            ApplicationException.when(True, str(error), self.log)

    def _conta_consumo_2_log(self, info_conta):
        self.log.info(f'==> Concessionária/Tipo Servico: {info_conta.concessionaria.name} / {info_conta.tipo_servico.name} ')
        self.log.info(f'==> Id Documento: {info_conta.id_documento}')
        self.log.info(f'==> Id Cliente: {info_conta.id_cliente}')
        self.log.info(f'==> Id Contribuinte: {info_conta.id_contribuinte}')
        self.log.info(f'==> Id Contrato: {info_conta.id_contrato}')
        self.log.info(f'==> Mes / periodo referencia: {info_conta.periodo_referencia}')
        self.log.info(f'==> Emissao/Vencimento: {info_conta.data_emissao} / {info_conta.data_vencimento}')
        self.log.info(f'==> Valor: {info_conta.valor}')
        self.log.info(info_conta.__dict__)

    def _list_pdf(self):
        return [f.upper() for f in os.listdir(self.downloaded_folder) if os.path.isfile(os.path.join(self.downloaded_folder, f)) and f.upper().endswith('.PDF') == True]

    def execute(self) -> Any:

        pool_alojamentos = self._get_alojamentos()

        processed_list = []
        ignored_list = []
        error_list = []
        files = self._list_pdf()
        for file_name in files:
            complete_file_name = os.path.join(self.downloaded_folder, file_name)
            self.log.info(f'Processing file: {complete_file_name}')
            all_text = PdfExtractor().get_text(complete_file_name)
            conta_consumo = ContaConsumoFactory().execute(all_text, file_name)
            if (conta_consumo):
                try:
                    conta_consumo.create(all_text)
                    alojamento = pool_alojamentos.get_alojamento(conta_consumo.id_cliente.strip(), conta_consumo.id_contrato.strip(), conta_consumo.local_consumo.strip())
                    if (alojamento):
                        conta_consumo.id_alojamento = alojamento.nome
                        conta_consumo.diretorio = alojamento.diretorio
                        processed_list.append(conta_consumo)
                    # self._conta_consumo_2_log(info_conta, log)

                except Exception as erro:
                    error_list.append(conta_consumo)
                    # self._conta_consumo_2_log(info_conta, log)

                # destination = os.path.join(self.processed_folder, file_name)
            else:
                msg = f'Arquivo não reconhecido ou fora do formato {complete_file_name}'
                self.log.info(msg)
                ignored_list.append((file_name, msg))
                # destination = os.path.join(self.errors_folder, file_name)

            # self._move_file(complete_file_name, destination, log)

        if (len(files)):
            self._result_2_excel(processed_list, error_list, ignored_list)


        for conta in processed_list:
            directory = self.drive.find_file(conta.diretorio, self.config.get('google drive.folder_client_id'))
            if (directory):
                continue
            else:
                self.drive.create_folder(conta.diretorio, self.config.get('google drive.folder_client_id'))

        return Any
