from pathlib import Path

ARTIFACT_DIR = Path("storage/artifacts")

CHUNKS = ARTIFACT_DIR / "chunks.pkl"

EMBEDDINGS = ARTIFACT_DIR / "chunk_embeddings.npy"

FAISS_INDEX = ARTIFACT_DIR / "chunk_faiss.index"

CASE_METADATA = ARTIFACT_DIR / "case_metadata.pkl"
