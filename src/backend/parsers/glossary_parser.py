import re
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import List, Dict, Tuple
from ..models import DocumentChunk
from .base import BaseDocumentParser

class GlossaryDocumentParser(BaseDocumentParser):
    def can_parse(self, file_path: Path) -> bool:
        return file_path.suffix.lower() == ".docx"

    def parse(self, file_path: Path) -> List[DocumentChunk]:
        paragraphs = self._read_docx_paragraphs(file_path)
        glossary_items = self._extract_glossary_items(paragraphs)
        return self._create_chunks(file_path, paragraphs, glossary_items)

    def _read_docx_paragraphs(self, file_path: Path) -> List[str]:
        with zipfile.ZipFile(file_path) as docx:
            tree = ET.fromstring(docx.read("word/document.xml"))
            ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
            paragraphs = []
            for p in tree.iterfind(".//w:p", ns):
                text = "".join(node.text for node in p.iterfind(".//w:t", ns) if node.text)
                if text.strip():
                    paragraphs.append(text.strip())
            return paragraphs

    def _extract_glossary_items(self, paragraphs: List[str]) -> List[Dict[str, str]]:
        items = []
        for index, line in enumerate(paragraphs):
            if " - " in line or ":" in line:
                parts = re.split(r"[\-\:]", line, 1)
                term = parts[0].strip()
                meaning = parts[1].strip() if len(parts) > 1 else ""
                items.append({"term": term, "meaning": meaning, "raw": line})
            elif index + 1 < len(paragraphs) and len(line) < 30 and len(paragraphs[index + 1]) > 20:
                items.append({
                    "term": line,
                    "meaning": paragraphs[index + 1],
                    "raw": f"{line}: {paragraphs[index + 1]}"
                })
        return items

    def _create_chunks(
        self,
        file_path: Path,
        paragraphs: List[str],
        items: List[Dict[str, str]]
    ) -> List[DocumentChunk]:
        chunks = []
        full_text = "\n".join(paragraphs)
        chunks.append(
            DocumentChunk(
                id="glossary_full",
                source_file=file_path.name,
                doc_type="Glossary",
                category="Oil and Gas Terms",
                title="Glosarium Singkatan dan Istilah Lengkap",
                content=full_text,
                metadata={"total_items": len(items)}
            )
        )

        chunk_size = 5
        for index in range(0, len(items), chunk_size):
            batch = items[index:index + chunk_size]
            batch_text = "\n".join(
                [f"- {item['term']}: {item['meaning']}" for item in batch if item["term"]]
            )
            terms_list = [item["term"] for item in batch if item["term"]]
            chunk_num = index // chunk_size + 1
            chunks.append(
                DocumentChunk(
                    id=f"glossary_chunk_{chunk_num}",
                    source_file=file_path.name,
                    doc_type="Glossary",
                    category="Oil and Gas Terms",
                    title=f"Glosarium Istilah Part {chunk_num}",
                    content=batch_text,
                    metadata={"terms": terms_list}
                )
            )
        return chunks
