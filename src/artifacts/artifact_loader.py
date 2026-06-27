from src.artifacts.artifact_paths import (
    CHUNKS,
    EMBEDDINGS,
    FAISS_INDEX
)

from src.indexing.storage import (
    load_chunks,
    load_embeddings,
    load_faiss_index
)

from src.indexing.faiss_index import FaissIndexer
from src.indexing.storage import load_case_metadata
from src.artifacts.artifact_paths import CASE_METADATA

class ArtifactLoader:
    def load(self):

        chunks = load_chunks(str(CHUNKS))
        embeddings = load_embeddings(str(EMBEDDINGS))
        faiss_index_raw = load_faiss_index(str(FAISS_INDEX))
        case_metadata = load_case_metadata(str(CASE_METADATA))

        dim = embeddings.shape[1]
        index = FaissIndexer(dim)
        index.load_existing_index(faiss_index_raw)

        return {
            "chunks": chunks,
            "embeddings": embeddings,
            "index": index,
            "case_metadata": case_metadata
        }
