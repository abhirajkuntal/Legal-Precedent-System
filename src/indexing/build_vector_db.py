import uuid
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams, PointStruct

from src.ingestion.loader import yield_all_cases
from src.preprocessing.chunker import split_into_chunks
from src.embedding.embedder import LegalEmbedder

def build_qdrant_index(data_dir: str, collection_name="legal_cases", batch_size=1000):
    # 1. Connect to the local Docker Qdrant instance
    client = QdrantClient("localhost", port=6333)
    
    embedder = LegalEmbedder()
    embedding_dim = 768  # Dimension for all-mpnet-base-v2

    # 2. Create the collection if it doesn't exist
    if not client.collection_exists(collection_name):
        client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(size=embedding_dim, distance=Distance.COSINE)
        )
        print(f"Created Qdrant collection: {collection_name}")

    current_chunks = []
    points_to_upsert = []
    total_processed = 0

    print("Starting streaming batch ingestion...")
    
    # 3. Consume the generator
    for case in yield_all_cases(data_dir):
        case_chunks = split_into_chunks(case)
        current_chunks.extend(case_chunks)

        # 4. Process when batch limit is reached
        if len(current_chunks) >= batch_size:
            total_processed = _process_and_upload_batch(
                client, embedder, collection_name, current_chunks, points_to_upsert, total_processed
            )

    # 5. Process any remaining chunks in the final partial batch
    if current_chunks:
        _process_and_upload_batch(
            client, embedder, collection_name, current_chunks, points_to_upsert, total_processed
        )
        
    print(f"Ingestion complete. Total chunks vectorized and stored: {total_processed}")

def _process_and_upload_batch(client, embedder, collection_name, chunks, points, total_count):
    # Extract text and generate dense embeddings
    texts = [chunk.chunk_text for chunk in chunks]
    embeddings = embedder.embed_texts(texts)

    # Build the payload structure for Qdrant
    for i, chunk in enumerate(chunks):
        points.append(
            PointStruct(
                id=str(uuid.uuid4()),  # Qdrant requires UUIDs or integers
                vector=embeddings[i].tolist(),
                payload={
                    "case_id": chunk.case_id,
                    "case_title": chunk.case_title,
                    "court": chunk.court,
                    "jurisdiction": chunk.jurisdiction,
                    "judges": chunk.judges,
                    "legal_category": chunk.legal_category,
                    "chunk_text": chunk.chunk_text,
                    "pagerank": chunk.pagerank
                }
            )
        )
        total_count += 1
    
    # Push the vectors and metadata to disk
    client.upsert(
        collection_name=collection_name,
        points=points
    )
    
    print(f"Upserted batch. Total chunks stored: {total_count}")
    
    # CRITICAL: Clear the lists to free up RAM for the next iteration
    chunks.clear()
    points.clear()
    
    return total_count

if __name__ == "__main__":
    # Point this to your raw JSON data folder
    build_qdrant_index("data/raw")
