from dataclasses import dataclass


@dataclass
class CaseChunk:

    chunk_id: str

    case_id: int

    case_title: str

    court: str

    jurisdiction: str

    judges: list[str]

    chunk_text: str

    chunk_index: int

    pagerank: float

    legal_category: str = ""

