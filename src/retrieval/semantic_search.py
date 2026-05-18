# src/retrieval/semantic_search.py

from src.embedding.embedder import LegalEmbedder
from src.indexing.faiss_index import FaissIndexer


class SemanticSearchEngine:

    def __init__(self, cases):

        self.cases = cases

        self.embedder = LegalEmbedder()

        print("Generating embeddings...")

        self.embeddings = self.embedder.embed_cases(
            cases
        )

        embedding_dim = self.embeddings.shape[1]

        print("Building FAISS index...")

        self.index = FaissIndexer(embedding_dim)

        self.index.add_embeddings(
            self.embeddings
        )

    def search(
        self,
        query: str,
        top_k=5
    ):

        query_embedding = self.embedder.embed_query(
            query
        )

        distances, indices = self.index.search(
            query_embedding,
            top_k=top_k
        )

        results = []

        for distance, idx in zip(distances, indices):

            case = self.cases[idx]

            results.append({
                "score": float(distance),
                "case": case
            })

        return results
