from pathlib import Path
import torch

# ============================================================
# DATASET
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

RAW_DATASET = PROJECT_ROOT / "data" / "raw"

# ============================================================
# OUTPUT DIRECTORY
# ============================================================

ARTIFACT_DIR = PROJECT_ROOT / "storage" / "artifacts"

ARTIFACT_DIR.mkdir(
    parents=True,
    exist_ok=True
)

# ============================================================
# SHARDS
# ============================================================

EMBEDDING_SHARD_DIR = ARTIFACT_DIR / "embedding_shards"

EMBEDDING_SHARD_DIR.mkdir(
    parents=True,
    exist_ok=True
)

# ============================================================
# CHECKPOINTS
# ============================================================

CHECKPOINT_FILE = (
    ARTIFACT_DIR / "pipeline_checkpoint.json"
)

LOG_FILE = (
    ARTIFACT_DIR / "pipeline.log"
)

# ============================================================
# PIPELINE PARAMETERS
# ============================================================

CHUNK_SIZE = 3

EMBED_BATCH_SIZE = 64

SHARD_SIZE = 10000

SAVE_INTERVAL = 500

# ============================================================
# EMBEDDING MODEL
# ============================================================

EMBEDDING_MODEL = (
    "sentence-transformers/all-MiniLM-L6-v2"
)

DEVICE = (
    "cuda"
    if torch.cuda.is_available()
    else "cpu"
)

# ============================================================
# FAISS
# ============================================================

FAISS_INDEX_NAME = "chunk_faiss.index"

HNSW_M = 32

HNSW_EF_CONSTRUCTION = 200
