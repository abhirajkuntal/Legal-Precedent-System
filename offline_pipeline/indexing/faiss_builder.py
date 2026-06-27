import faiss
import numpy as np

def build_faiss(embeddings):
    dim = embeddings.shape[1]

    index = faiss.IndexHNSWFlat(dim, 32)  # better than FlatL2
    index.hnsw.efConstruction = 200

    index.add(np.array(embeddings).astype("float32"))
    return index


def save_index(index, path):
    faiss.write_index(index, str(path))
