# offline_pipeline/processing/chunker.py

from src.schemas.chunk_schema import CaseChunk

def chunk_case(case, chunk_size=3):
    paragraphs = [
        p.strip()
        for p in case["opinion_text"].split("\n")
        if p.strip()
    ]

    chunks = []

    for i in range(0, len(paragraphs), chunk_size):
        group = paragraphs[i:i+chunk_size]
        text = "\n\n".join(group)

        chunks.append(
            CaseChunk(
                chunk_id=f"{case['case_id']}_{i}",
                case_id=case["case_id"],
                case_title=case["title"],
                court=case.get("court", ""),
                jurisdiction=case.get("jurisdiction", ""),
                judges=case.get("judges", []),
                chunk_text=text,
                chunk_index=i,
                pagerank=case.get("pagerank", 0.0),
                legal_category=""
            )
        )

    return chunks
