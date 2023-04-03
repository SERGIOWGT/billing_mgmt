from dataclasses import dataclass, field
from pyparsing import List

@dataclass
class PageContent:
    lines: List[str] = field(default_factory=list)
