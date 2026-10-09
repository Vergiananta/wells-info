from typing import List
import numpy as np
from openai import OpenAI
from ..config import settings

class EmbeddingService:
    def __init__(self, client: OpenAI = None, model: str = None):
        api_key = settings.openai_api_key
        self._client = client or OpenAI(api_key=api_key)
        self._model = model or settings.embedding_model

    def embed_texts(self, texts: List[str]) -> np.ndarray:
        cleaned_texts = [text.replace("\n", " ")[:8000] for text in texts]
        response = self._client.embeddings.create(
            input=cleaned_texts,
            model=self._model
        )
        return np.array([item.embedding for item in response.data], dtype=np.float32)

    def embed_query(self, query: str) -> np.ndarray:
        return self.embed_texts([query])[0]
