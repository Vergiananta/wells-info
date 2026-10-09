from abc import ABC, abstractmethod
from pathlib import Path
from typing import List
from ..models import DocumentChunk

class BaseDocumentParser(ABC):
    @abstractmethod
    def can_parse(self, file_path: Path) -> bool:
        pass

    @abstractmethod
    def parse(self, file_path: Path) -> List[DocumentChunk]:
        pass
