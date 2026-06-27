import json
import numpy as np
from pathlib import Path

def append_chunks(path, chunks):
    with open(path, "a", encoding="utf-8") as f:
        for c in chunks:
            f.write(json.dumps(c.__dict__) + "\n")


def save_embeddings(path, embeddings):
    if Path(path).exists():
        old = np.load(path)
        embeddings = np.vstack([old, embeddings])
    np.save(path, embeddings)
