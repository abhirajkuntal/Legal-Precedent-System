from src.schemas.chunk_schema import CaseChunk
from src.legal.legal_classifier import LegalClassifier

classifier = LegalClassifier()

def split_into_chunks(
    case,
    paragraphs_per_chunk=3
):

    paragraphs = [
        p.strip()
        for p in case.opinion_text.split("\n")
        if p.strip()
    ]

    pagerank = case.pagerank

    chunks = []

    for i in range(
        0,
        len(paragraphs),
        paragraphs_per_chunk
    ):

        group = paragraphs[
            i:i + paragraphs_per_chunk
        ]

        chunk_text = "\n\n".join(group)

        legal_category = classifier.classify(
            chunk_text )

        chunk = CaseChunk(
            chunk_id=f"{case.case_id}_{i}",

            case_id=case.case_id,

            case_title=case.title,

            court=case.court,

            jurisdiction=case.jurisdiction,

            judges=case.judges,

            chunk_text=chunk_text,

            chunk_index=i,

            pagerank=pagerank,

            legal_category=legal_category
        )

        chunks.append(chunk)

    return chunks
