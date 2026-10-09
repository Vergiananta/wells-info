import os
from pathlib import Path
from typing import List
from ..config import Settings, settings
from ..models import DocumentChunk
from ..parsers.base import BaseDocumentParser
from ..parsers.glossary_parser import GlossaryDocumentParser
from ..parsers.pdf_parser import PdfWellsDocumentParser
from ..repositories.json_repository import JsonDocumentRepository
from ..repositories.database_repository import SqliteDatabaseRepository
from ..repositories.embedding_repository import EmbeddingCacheRepository
from .embedding_service import EmbeddingService
from .retrieval_service import HybridRetrievalService
from .chat_service import ChatRagService

class WellsPipelineService:
    def __init__(self, app_settings: Settings = None):
        self._settings = app_settings or settings
        self._parsers: List[BaseDocumentParser] = [
            GlossaryDocumentParser(),
            PdfWellsDocumentParser()
        ]
        self._json_repo = JsonDocumentRepository(self._settings.json_output_path)
        self._db_repo = SqliteDatabaseRepository(self._settings.sqlite_db_path)
        self._embedding_repo = EmbeddingCacheRepository(self._settings.embedding_cache_path)
        self._embedding_service = EmbeddingService(model=self._settings.embedding_model)
        
        self._chunks: List[DocumentChunk] = []
        self._retrieval_service: HybridRetrievalService = None
        self._chat_service: ChatRagService = None

    def initialize(self, force_reparse: bool = False) -> None:
        if not force_reparse and self._can_load_from_cache():
            self._load_from_cache()
        else:
            self._execute_full_ingestion()

        self._retrieval_service = HybridRetrievalService(
            chunks=self._chunks,
            embeddings=self._embedding_repo.load(),
            embedding_service=self._embedding_service
        )
        self._chat_service = ChatRagService(
            retrieval_service=self._retrieval_service,
            model=self._settings.chat_model
        )

    def parse_all_documents(self) -> List[DocumentChunk]:
        chunks: List[DocumentChunk] = []

        if self._settings.glossary_path.exists():
            for parser in self._parsers:
                if parser.can_parse(self._settings.glossary_path):
                    chunks.extend(parser.parse(self._settings.glossary_path))
                    break

        if self._settings.datasets_dir.exists():
            for root, _, files in os.walk(self._settings.datasets_dir):
                for filename in sorted(files):
                    file_path = Path(root) / filename
                    for parser in self._parsers:
                        if parser.can_parse(file_path):
                            chunks.extend(parser.parse(file_path))
                            break

        return chunks

    def ask(self, query: str, top_k: int = 5):
        if self._chat_service is None:
            self.initialize()
        return self._chat_service.answer_query(query, top_k=top_k)

    def _can_load_from_cache(self) -> bool:
        return (
            self._json_repo.exists()
            and self._embedding_repo.exists()
        )

    def _load_from_cache(self) -> None:
        self._chunks = self._json_repo.load()

    def _execute_full_ingestion(self) -> None:
        self._chunks = self.parse_all_documents()
        self._json_repo.save(self._chunks)
        self._db_repo.save_all(self._chunks)

        chunk_texts = [
            f"Dokumen: {chunk.source_file} | Konten: {chunk.content}"
            for chunk in self._chunks
        ]
        embeddings = self._embedding_service.embed_texts(chunk_texts)
        self._embedding_repo.save(embeddings)
