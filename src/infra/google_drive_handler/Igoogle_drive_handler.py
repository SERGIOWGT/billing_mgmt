from typing import Any, List, Optional
from abc import ABC, abstractmethod

class IGoogleDriveHandler(ABC):

    @abstractmethod
    def get_file(self, file_id: str) -> bytes:
        ...

    @abstractmethod
    def get_files(self, folder_id: str) -> bytes:
        ...

    @abstractmethod
    def get_google_sheets_file(self, file_id: str) -> bytes:
        ...

    @abstractmethod
    def upload_file(self, local_file_name: str,  file_name: str, parents: List, mime_type: str='') -> Any:
        ...

    @abstractmethod
    def update_file(self, file_id, new_filename: str):
        ...

    @abstractmethod
    def find_file(self, name: str, parent_id: str = '') -> Optional[Any]:
        ...

    @abstractmethod
    def create_folder(self, name, parent_id: str = '') -> Any:
        ...
