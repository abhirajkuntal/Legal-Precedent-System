from src.ingestion.loader import load_all_cases
from src.artifacts.artifact_builder import ArtifactBuilder


def main():

    print("===================================")
    print("OFFLINE PIPELINE STARTING")
    print("===================================")

    # 1. Load raw data
    cases = load_all_cases("data/raw")
    print(f"Loaded cases: {len(cases)}")

    # 2. Build artifacts
    builder = ArtifactBuilder()

    print("Building chunks...")
    chunks = builder.build_chunks(cases)

    print("Building embeddings...")
    embeddings = builder.build_embeddings(chunks)

    print("Building FAISS index...")
    index = builder.build_faiss(embeddings)

    print("Building BM25 index... (inside loader)")
    # BM25 usually built online too, but safe here if you want consistency

    print("Building case metadata...")
    case_metadata = builder.build_case_metadata(cases)

    # 3. SAVE EVERYTHING
    print("Saving artifacts...")
    builder.save(
        chunks=chunks,
        embeddings=embeddings,
        index=index,
        cases=cases
    )

    print("===================================")
    print("OFFLINE PIPELINE COMPLETE")
    print("===================================")


if __name__ == "__main__":
    main()
