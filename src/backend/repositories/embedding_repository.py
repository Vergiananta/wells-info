from pathlib import Path
from typing import Optional
import numpy as np

class EmbeddingCacheRepository:
    def __init__(self, cache_path: Path):
        self._cache_path = cache_path

    def save(self, embeddings: np.ndarray) -> None:
        self._cache_path.parent.mkdir(parents=True, exist_ok=True)
        np.savez_compressed(self._cache_path, embeddings=embeddings)

    def load(self) -> Optional[np.ndarray]:
        if not self._cache_path.exists():
            return None
        data = np.load(self._cache_path)
        return data["embeddings"]

    def exists(self) -> bool:
        return self._cache_path.exists()
