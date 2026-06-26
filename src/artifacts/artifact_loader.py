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


class ArtifactLoader:

    def load(self):

        print("Loading artifacts...")

        chunks = load_chunks(str(CHUNKS))
        embeddings = load_embeddings(str(EMBEDDINGS))
        faiss_index_raw = load_faiss_index(str(FAISS_INDEX))

        dim = embeddings.shape[1]

        index = FaissIndexer(dim)
        index.load_existing_index(faiss_index_raw)

        return {
            "chunks": chunks,
            "embeddings": embeddings,
            "index": index
        }
