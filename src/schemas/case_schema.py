from dataclasses import dataclass
from typing import List


@dataclass
class NormalizedCase:
    case_id: int

    title: str
    title_abbreviation: str

    court: str
    jurisdiction: str

    decision_date: str
    docket_number: str

    judges: List[str]
    parties: List[str]
    attorneys: List[str]

    citations: List[str]
    cited_cases: List[str]

    opinion_text: str
    head_matter: str

    search_text: str

    pagerank: float = 0.0
