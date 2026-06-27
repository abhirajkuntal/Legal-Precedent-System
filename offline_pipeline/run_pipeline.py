# offline_pipeline/run_pipeline.py

from offline_pipeline.loaders.case_loader import load_cases
from offline_pipeline.processing.chunker import chunk_case
from offline_pipeline.processing.embedder import Embedder
from offline_pipeline.storage.writer import append_chunks, save_embeddings
from offline_pipeline.indexing.faiss_builder import build_faiss, save_index
from offline_pipeline.config import *
from offline_pipeline.logger import logger
import numpy as np


def main():

    logger.info("STARTING OFFLINE PIPELINE")

    embedder = Embedder()

    all_embeddings = []
    all_chunks = []

    batch_texts = []
    batch_chunks = []

    for case in load_cases(RAW_DIR):

        chunks = chunk_case(case)

        for chunk in chunks:
            batch_texts.append(chunk.chunk_text)
            batch_chunks.append(chunk)

            if len(batch_texts) >= BATCH_SIZE_EMBEDDING:

                embeddings = embedder.embed_batch(batch_texts)

                save_embeddings(EMBEDDINGS_PATH, embeddings)
                append_chunks(CHUNKS_PATH, batch_chunks)

                all_embeddings.append(embeddings)

                batch_texts = []
                batch_chunks = []

    # final flush
    if batch_texts:
        embeddings = embedder.embed_batch(batch_texts)
        save_embeddings(EMBEDDINGS_PATH, embeddings)
        append_chunks(CHUNKS_PATH, batch_chunks)
        all_embeddings.append(embeddings)

    logger.info("BUILDING FAISS INDEX")

    final_embeddings = np.vstack(all_embeddings).astype("float32")

    index = build_faiss(final_embeddings)
    save_index(index, INDEX_PATH)

    logger.info("PIPELINE COMPLETE")


if __name__ == "__main__":
    main()
