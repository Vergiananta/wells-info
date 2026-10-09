import re
from pathlib import Path
from typing import List, Dict, Any
import pypdf
from ..models import DocumentChunk
from .base import BaseDocumentParser

class PdfWellsDocumentParser(BaseDocumentParser):
    def can_parse(self, file_path: Path) -> bool:
        return file_path.suffix.lower() == ".pdf"

    def parse(self, file_path: Path) -> List[DocumentChunk]:
        reader = pypdf.PdfReader(str(file_path))
        total_pages = len(reader.pages)
        chunks = []
        full_text = ""

        doc_type = "DGOS" if "DGOS" in file_path.name else "DDR"

        for page_idx, page in enumerate(reader.pages):
            page_text = page.extract_text() or ""
            full_text += f"\n--- Page {page_idx + 1} ---\n" + page_text
            cleaned_text = re.sub(r" +", " ", page_text).strip()

            chunks.append(
                DocumentChunk(
                    id=f"{file_path.stem}_p{page_idx + 1}",
                    source_file=file_path.name,
                    doc_type=doc_type,
                    page=page_idx + 1,
                    total_pages=total_pages,
                    content=cleaned_text,
                    metadata={"source_file": file_path.name, "page": page_idx + 1}
                )
            )

        metadata = self._extract_metadata(file_path.name, full_text)
        summary_chunk = DocumentChunk(
            id=f"{file_path.stem}_summary",
            source_file=file_path.name,
            doc_type="Document Summary",
            page=0,
            total_pages=total_pages,
            content=(
                f"Dokumen: {file_path.name}\n"
                f"Well Name: {metadata.get('well_name', 'BARAKUDA-1')}\n"
                f"Lokasi / Region / Country: {metadata.get('country', 'Malaysia')} ({metadata.get('region', 'PM Block PM515')})\n"
                f"Ringkasan Isi & Metadata:\n{full_text[:1200]}"
            ),
            metadata=metadata
        )
        chunks.insert(0, summary_chunk)
        return chunks

    def _extract_metadata(self, filename: str, text: str) -> Dict[str, Any]:
        metadata: Dict[str, Any] = {}
        if "BARAKUDA-1" in text or "BARAKUDA" in filename:
            metadata["well_name"] = "BARAKUDA-1"

        region_match = re.search(r"Region\s*:\s*([A-Za-z0-9\-\_]+)", text)
        if region_match:
            metadata["region"] = region_match.group(1).strip()
        if "PM" in text or "PM515" in text:
            metadata["region"] = "PM (Peninsular Malaysia)"
            metadata["country"] = "Malaysia"

        block_match = re.search(r"Block\s*:\s*([A-Za-z0-9\-\_]+)", text)
        if block_match:
            metadata["block"] = block_match.group(1).strip()

        npt_matches = re.findall(r"NPT[\:\s]+([^\n\r]+)", text, re.IGNORECASE)
        if npt_matches:
            metadata["npt_info"] = [m.strip() for m in npt_matches if m.strip()]

        wl_matches = re.findall(
            r"(WL Run[^\.\n\r]+|Wireline[^\.\n\r]+|Perform WL[^\.\n\r]+)",
            text,
            re.IGNORECASE
        )
        if wl_matches:
            metadata["wireline_info"] = [w.strip() for w in wl_matches]

        return metadata
