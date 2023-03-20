from dataclasses import dataclass
from typing import Any
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

@dataclass
class GDriveHandler():
    g_login: Any = None
    drive: GoogleDrive = None
    

    def connect(self):
        self.g_login = GoogleAuth()
        self.g_login.LocalWebserverAuth()
        self.drive = GoogleDrive(self.g_login)
            
    def download_file(self, file_id: str):
        file_id = '1ECbR1_6tlkhVijUYTL4ATI7cw7bt1GFq'
        fileDownloaded = self.drive.CreateFile({'id': file_id})
        fileDownloaded.GetContentFile('Alojamentos.xl')
