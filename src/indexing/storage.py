import pickle
import numpy as np
import faiss


def save_chunks(chunks, path):

    with open(path, "wb") as f:
        pickle.dump(chunks, f)


def load_chunks(path):

    with open(path, "rb") as f:
        return pickle.load(f)


def save_embeddings(embeddings, path):

    np.save(path, embeddings)


def load_embeddings(path):

    return np.load(path)


def save_faiss_index(index, path):

    if hasattr(index, "index"):
        faiss.write_index(index.index, path)
    else:
        faiss.write_index(index, path)

def load_faiss_index(path):

    return faiss.read_index(path)

def save_case_metadata(metadata, path):
    with open(path, "wb") as f:
        pickle.dump(metadata,f)

def load_case_metadata(path):
    with open(path, "rb") as f:
        return pickle.load(f)

