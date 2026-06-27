from pathlib import Path

DATA_DIR = Path("data")
RAW_DIR = DATA_DIR / "raw"

ARTIFACT_DIR = DATA_DIR / "artifacts"
CHUNKS_PATH = ARTIFACT_DIR / "chunks.jsonl"
EMBEDDINGS_PATH = ARTIFACT_DIR / "embeddings.npy"
METADATA_PATH = ARTIFACT_DIR / "case_metadata.pkl"
INDEX_PATH = ARTIFACT_DIR / "faiss.index"

BATCH_SIZE_EMBEDDING = 64
CHUNK_SIZE = 3

EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
