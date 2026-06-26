from src.preprocessing.chunker import split_into_chunks
from src.embedding.embedder import LegalEmbedder
from src.indexing.faiss_index import FaissIndexer
from src.indexing.storage import (
    save_chunks,
    save_embeddings,
    save_faiss_index
)

from src.artifacts.artifact_paths import (
    CHUNKS,
    EMBEDDINGS,
    FAISS_INDEX
)

from src.artifacts.case_metadata_builder import CaseMetadataBuilder
from src.indexing.storage import save_case_metadata
from src.artifacts.artifact_paths import CASE_METADATA

class ArtifactBuilder:

    def __init__(self):
        self.embedder = LegalEmbedder()

    # -----------------------------
    # STEP 1: CHUNKS
    # -----------------------------
    def build_chunks(self, cases):
        chunks = []
        for case in cases:
            chunks.extend(split_into_chunks(case))
        return chunks

    # -----------------------------
    # STEP 2: EMBEDDINGS
    # -----------------------------
    def build_embeddings(self, chunks):

        print("Generating embeddings...")

        texts = [c.chunk_text for c in chunks]

        embeddings = self.embedder.embed_texts(texts)

        return embeddings

    # -----------------------------
    # STEP 3: FAISS
    # -----------------------------
    def build_faiss(self, embeddings):

        print("Building FAISS index...")

        dim = embeddings.shape[1]

        index = FaissIndexer(dim)
        index.add_embeddings(embeddings)

        return index

    #Building case Metadata
    def build_case_metadata(self, cases):

        builder = CaseMetadataBuilder()
        metadata = builder.build(cases)

        return metadata

    # -----------------------------
    # STEP 4: SAVE EVERYTHING
    # -----------------------------
    def save(self, chunks, embeddings, index, cases):

        metadata = self.build_case_metadata(cases)

        save_chunks(chunks, str(CHUNKS))
        save_embeddings(embeddings, str(EMBEDDINGS))
        save_faiss_index(index, str(FAISS_INDEX))
        save_case_metadata(metadata, str(CASE_METADATA))    

