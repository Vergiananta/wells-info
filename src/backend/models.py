from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

@dataclass
class DocumentChunk:
    id: str
    source_file: str
    doc_type: str
    content: str
    page: int = 0
    total_pages: int = 0
    title: Optional[str] = None
    category: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "source_file": self.source_file,
            "doc_type": self.doc_type,
            "content": self.content,
            "page": self.page,
            "total_pages": self.total_pages,
            "title": self.title,
            "category": self.category,
            "metadata": self.metadata
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DocumentChunk":
        return cls(
            id=data["id"],
            source_file=data["source_file"],
            doc_type=data.get("doc_type", "General"),
            content=data["content"],
            page=data.get("page", 0),
            total_pages=data.get("total_pages", 0),
            title=data.get("title"),
            category=data.get("category"),
            metadata=data.get("metadata", {})
        )

@dataclass
class RetrievalItem:
    chunk: DocumentChunk
    score: float
    vector_score: float
    keyword_score: float

@dataclass
class ChatAnswer:
    query: str
    answer: str
    sources: List[str]
    retrieved_items: List[RetrievalItem]
