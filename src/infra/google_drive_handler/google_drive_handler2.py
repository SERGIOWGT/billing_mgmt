from typing import Any, Optional
from pydrive.auth import GoogleAuth
from .Igoogle_drive_handler import IGoogleDriveHandler


class GoogleDriveHandler2 (IGoogleDriveHandler):
    _drive = None

    def __init__(self):
        self._drive = GoogleAuth()
        self._drive.LocalWebserverAuth()  # Creates local webserver and auto handles authentication.

    def get_excel_file(self, file_id: str):
        ...

    def get_google_sheets_file(self, file_id: str):
        ...

    def upload_file(self, local_file_name: str,  file_name: str, parents=[]):
        ...

    def find_file(self, name: str, parent_id: str = '') -> Optional[Any]:
        ...

    def create_folder(self, name, parent_id: str = '') -> Any:
        ...


# drive = GoogleDriveHandler('./credentials')
