from abc import ABC, abstractmethod
from .pdf_content import PdfContent


class IPdfExtractorHandler(ABC):
    @abstractmethod
    def get_content(self, file_name: str, break_lines: bool = True) -> PdfContent:
        ...

    @staticmethod
    @abstractmethod
    def get_text(file_name: str) -> str:
        ...
