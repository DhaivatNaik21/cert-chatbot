from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent

DOC_DIR = BASE_DIR / "documents" / "cert data"
CHROMA_DIR = BASE_DIR / "chroma_db"
ENV_FILE = BASE_DIR / ".env"

COLLECTION_NAME = "cert_docs"

EMBEDDING_MODEL = "all-MiniLM-L6-v2"
GENERATION_MODEL = "openai/gpt-oss-20b"

CHUNK_SIZE = 512
CHUNK_OVERLAP = 100
CHUNK_SEPARATORS = ["\n\n", "\n", " ", ""]

TOP_K = 5
GENERATION_TEMPERATURE = 0.1