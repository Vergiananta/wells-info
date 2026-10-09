import json
import sqlite3
from pathlib import Path
from typing import List, Dict, Any
from ..models import DocumentChunk

class SqliteDatabaseRepository:
    def __init__(self, db_path: Path):
        self._db_path = db_path

    def _get_connection(self) -> sqlite3.Connection:
        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        return sqlite3.connect(self._db_path)

    def initialize_schema(self) -> None:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS parsed_documents (
                    id TEXT PRIMARY KEY,
                    source_file TEXT,
                    doc_type TEXT,
                    page INTEGER,
                    content TEXT,
                    metadata_json TEXT
                )
            """)
            cursor.execute("""
                CREATE VIRTUAL TABLE IF NOT EXISTS documents_fts USING fts5(
                    id,
                    source_file,
                    content
                )
            """)
            conn.commit()

    def save_all(self, chunks: List[DocumentChunk]) -> None:
        self.initialize_schema()
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM parsed_documents")
            cursor.execute("DELETE FROM documents_fts")
            for chunk in chunks:
                cursor.execute("""
                    INSERT INTO parsed_documents (id, source_file, doc_type, page, content, metadata_json)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    chunk.id,
                    chunk.source_file,
                    chunk.doc_type,
                    chunk.page,
                    chunk.content,
                    json.dumps(chunk.metadata)
                ))
                cursor.execute("""
                    INSERT INTO documents_fts (id, source_file, content)
                    VALUES (?, ?, ?)
                """, (chunk.id, chunk.source_file, chunk.content))
            conn.commit()

    def search_fts(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute("""
                    SELECT id, source_file, content, rank
                    FROM documents_fts
                    WHERE documents_fts MATCH ?
                    ORDER BY rank
                    LIMIT ?
                """, (query, limit))
                rows = cursor.fetchall()
                return [
                    {"id": r[0], "source_file": r[1], "content": r[2], "rank": r[3]}
                    for r in rows
                ]
            except sqlite3.OperationalError:
                return []
