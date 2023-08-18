#
# CLASSE QUE APENAS LÊ O PDF E O TRANSFORMA EM UM GRANDE TEXTO EM MEMORIA
#

#
# ESTRUTURAS DE DADOS USADAS PELO PDF EXTRATOR HANDLES USADAS COMO CLASSES
#
from dataclasses import dataclass, field
from pyparsing import List
import pypdfium2 as pdfium

@dataclass
class PageContent:
    lines: List[str] = field(default_factory=list)


@dataclass
class PdfContent:
    num_pages: int = 0
    pages: List[PageContent] = field(default_factory=list)

@dataclass
class PdfExtractorHandler ():

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
            text_all = textpage.get_text_range().encode('latin-1')
            page_content = PageContent()
            if break_lines:
                page_content.lines = text_all.split('\n')
            else:
                page_content.lines.append(text_all)

            result.pages.append(page_content)

        return result

    @staticmethod
    def get_text(file_name: str) -> str:
        doc = pdfium.PdfDocument(file_name, None)
        page_count = len(doc)  # get page counts

        all_text = ''
        pdf = pdfium.PdfDocument(file_name)
        for index in range(page_count):
            page = pdf.get_page(index)
            textpage = page.get_textpage()
            _text = textpage.get_text_range()
            all_text += ' ' + _text

        return all_text
