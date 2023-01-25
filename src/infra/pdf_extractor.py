from typing import List
import pypdfium2 as pdfium
from dataclasses import dataclass, field

@dataclass
class PageContent:
    lines: List[str] = field(default_factory=list)

@dataclass
class PdfContent:
    num_pages: int = 0
    pages: List[PageContent] = field(default_factory=list)

@dataclass
class PdfExtractor:

    def get_content(self, file_name: str, break_lines: bool = True) -> PdfContent:
        doc = pdfium.FPDF_LoadDocument(file_name, None)
        page_count = pdfium.FPDF_GetPageCount(doc)  # get page counts
        assert(page_count >= 1)

        result = PdfContent()
        result.num_pages = page_count
        result.pages = []

        pdf = pdfium.PdfDocument(file_name)
        for index in range(page_count):
            page = pdf.get_page(index)
            textpage = page.get_textpage()
            text_all = textpage.get_text_range()
            page_content = PageContent()
            if break_lines:
                page_content.lines = text_all.split('\n')
            else:
                page_content.lines.append(text_all)

            result.pages.append(page_content)

        return result

    @staticmethod
    def get_text(file_name: str) -> str:
        doc = pdfium.FPDF_LoadDocument(file_name, None)
        page_count = pdfium.FPDF_GetPageCount(doc)  # get page counts

        all_text = ''
        pdf = pdfium.PdfDocument(file_name)
        for index in range(page_count):
            page = pdf.get_page(index)
            textpage = page.get_textpage()
            all_text += ' ' + textpage.get_text_range()
            
        return all_text
