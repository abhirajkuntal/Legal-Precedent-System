import faiss
import numpy as np


class FaissIndexer:

    def __init__(self, embedding_dim):

        self.index = faiss.IndexFlatL2(
            embedding_dim
        )

    def add_embeddings(self, embeddings):

        self.index.add(
            np.array(embeddings).astype("float32")
        )

    def search(
        self,
        query_embedding,
        top_k=5
    ):

        distances, indices = self.index.search(
            np.array([query_embedding]).astype("float32"),
            top_k
        )

        return distances[0], indices[0]

    def load_existing_index(self, index):

        self.index = index
