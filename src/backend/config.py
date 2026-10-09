import os
from pathlib import Path
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

@dataclass(frozen=True)
class Settings:
    base_dir: Path = Path(__file__).resolve().parent.parent.parent
    datasets_dir: Path = base_dir / "Datasets"
    glossary_path: Path = base_dir / "Glossaries.docx"
    output_dir: Path = base_dir / "output"
    
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    embedding_model: str = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
    chat_model: str = os.getenv("OPENAI_CHAT_MODEL", "gpt-4o-mini")
    
    json_output_path: Path = output_dir / "parsed_wells_data.json"
    sqlite_db_path: Path = output_dir / "wells_data.db"
    embedding_cache_path: Path = output_dir / "embeddings_cache.npz"

settings = Settings()
