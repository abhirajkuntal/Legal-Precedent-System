from offline_pipeline.config import ARTIFACT_DIR

CHUNK_FILE = (
    ARTIFACT_DIR / "chunks.jsonl"
)

CASE_METADATA = (
    ARTIFACT_DIR / "case_metadata.pkl"
)

FAISS_INDEX = (
    ARTIFACT_DIR / "chunk_faiss.index"
)

MERGED_EMBEDDINGS = (
    ARTIFACT_DIR / "chunk_embeddings.npy"
)
