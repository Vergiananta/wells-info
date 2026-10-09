import json
from pathlib import Path
from typing import List
from ..models import DocumentChunk

class JsonDocumentRepository:
    def __init__(self, file_path: Path):
        self._file_path = file_path

    def save(self, chunks: List[DocumentChunk]) -> None:
        self._file_path.parent.mkdir(parents=True, exist_ok=True)
        raw_data = [chunk.to_dict() for chunk in chunks]
        with open(self._file_path, "w", encoding="utf-8") as file:
            json.dump(raw_data, file, indent=2, ensure_ascii=False)

    def load(self) -> List[DocumentChunk]:
        if not self._file_path.exists():
            return []
        with open(self._file_path, "r", encoding="utf-8") as file:
            raw_data = json.load(file)
            return [DocumentChunk.from_dict(item) for item in raw_data]

    def exists(self) -> bool:
        return self._file_path.exists()
