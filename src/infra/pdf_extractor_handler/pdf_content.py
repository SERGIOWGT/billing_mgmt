
from dataclasses import dataclass, field
from pyparsing import List
from .page_content import PageContent

@dataclass
class PdfContent:
    num_pages: int = 0
    pages: List[PageContent] = field(default_factory=list)
