import os
from typing import List, Any
import io
import pandas as pd
from src.infra.google_drive_handler.google_drive_handler import GoogleDriveHandler
from src.infra.repositorios.alojamentos.classes import Accommodation2

class AccommodationRepository:
    _accommodations: List[Accommodation2] = None

    def from_excel(self, stream_file: Any)  -> None:

        df_ = pd.read_excel(io.BytesIO(stream_file), sheet_name="#LISTA_GERAL")
        df = df_.where(pd.notnull(df_), None)
        cols = df.shape[1]
        expected_columns = ['Name', 'Value', 'Explanation']
        actual_columns = df.columns.tolist()




def main()->None:
    config_directory = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config')
    google_drive_handler = GoogleDriveHandler(config_directory)
    stream_file = google_drive_handler.get_excel_file('1KLqmDAI79viSYAC64CyEqC84BxTcNqgq_vHdVE9FI3w')
    
    repo = AccommodationRepository()
    repo.from_excel(stream_file)
    
    
    

main()