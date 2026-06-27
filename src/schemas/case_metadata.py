from dataclasses import dataclass


@dataclass
class CaseMetadata:

    case_id: int

    title: str

    court: str

    jurisdiction: str

    judges: list[str]

    head_matter: str

    opinion_text: str

    pagerank: float
