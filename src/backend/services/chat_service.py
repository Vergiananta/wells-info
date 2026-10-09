from typing import List, Set
from openai import OpenAI
from ..config import settings
from ..models import ChatAnswer, RetrievalItem
from .retrieval_service import HybridRetrievalService

class ChatRagService:
    SYSTEM_PROMPT = """Anda adalah AI Asisten Ahli Data Operasional Sumur & Glosarium Oil & Gas (Wells & Petroleum AI Specialist).

TUGAS UTAMA:
1. Jawab pertanyaan pengguna HANYA berdasarkan KELENGKAPAN INFORMASI dari KONTEKS DOKUMEN yang diberikan.
2. WAJIB menyertakan NAMA FILE SUMBER yang relevan pada akhir jawaban dalam format:
   `[Sumber: <nama_file.pdf atau Glossaries.docx>]`
3. Jawab dengan ringkas, padat, faktual, dan sangat akurat sesuai data.

ATURAN GUARDRAIL (PENOLAKAN DI LUAR CAKUPAN):
- Jika pertanyaan pengguna di luar lingkup informasi sumur, operasi migas, atau istilah glosarium yang ada dalam dokumen (misal: topik umum, hiburan, resep masakan, dll.), TOLAK DENGAN PESAN KONSISTEN:
  "Maaf, pertanyaan Anda berada di luar cakupan data yang tersedia. Saya hanya dapat menjawab pertanyaan seputar operasional sumur (BARAKUDA-1, DGOS, DDR/DOR) dan glosarium istilah Oil & Gas yang tersedia di dataset."
- Jangan pernah mengarang data (no hallucination). Jika informasi tidak ada di dokumen, sampaikan bahwa informasi tidak ditemukan dalam dataset.
"""

    def __init__(
        self,
        retrieval_service: HybridRetrievalService,
        client: OpenAI = None,
        model: str = None
    ):
        self._retrieval_service = retrieval_service
        self._client = client or OpenAI(api_key=settings.openai_api_key)
        self._model = model or settings.chat_model

    def answer_query(self, query: str, top_k: int = 5) -> ChatAnswer:
        retrieval_items = self._retrieval_service.retrieve(query, top_k=top_k)
        context_string, sources = self._build_context(retrieval_items)
        user_prompt = self._build_user_prompt(query, context_string)

        response = self._client.chat.completions.create(
            model=self._model,
            messages=[
                {"role": "system", "content": self.SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.0
        )

        answer_text = response.choices[0].message.content or ""
        return ChatAnswer(
            query=query,
            answer=answer_text,
            sources=list(sources),
            retrieved_items=retrieval_items
        )

    def _build_context(self, items: List[RetrievalItem]) -> tuple[str, Set[str]]:
        context_parts = []
        sources: Set[str] = set()
        for idx, item in enumerate(items):
            chunk = item.chunk
            sources.add(chunk.source_file)
            page_info = f"Halaman: {chunk.page}" if chunk.page > 0 else "Summary/Dokumen"
            context_parts.append(
                f"\n--- DOKUMEN {idx + 1}: {chunk.source_file} ({page_info}) ---\n{chunk.content}\n"
            )
        return "".join(context_parts), sources

    def _build_user_prompt(self, query: str, context: str) -> str:
        return f"Konteks Dokumen yang Ditemukan:\n{context}\n\nPertanyaan Pengguna: {query}\nBerikan jawaban terbaik berdasarkan konteks di atas:"
