import json
from pathlib import Path

from src.schemas.case_schema import NormalizedCase


def extract_opinion_text(case_data: dict) -> str:
    opinions = case_data.get("casebody", {}).get("opinions", [])

    texts = []

    for opinion in opinions:
        text = opinion.get("text", "")
        if text:
            texts.append(text)

    return "\n\n".join(texts)


def construct_search_text(case: NormalizedCase) -> str:

    sections = [
        f"CASE TITLE: {case.title}",
        f"COURT: {case.court}",
        f"JURISDICTION: {case.jurisdiction}",
        f"LEGAL OPINION: {case.opinion_text}",
    ]

    return "\n\n".join(sections)

def parse_case_file(file_path: str) -> NormalizedCase:

    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    citations = [
        c.get("cite", "")
        for c in data.get("citations", [])
    ]

    cited_cases = [
        c.get("cite", "")
        for c in data.get("cites_to", [])
    ]

    pagerank = data.get(
        "analysis",
        {}
    ).get(
        "pagerank",
        {}
    ).get(
        "percentile",
        0.0
    )
    opinion_text = extract_opinion_text(data)

    case = NormalizedCase(


        case_id=data.get("id"),

        title=data.get("name", ""),
        title_abbreviation=data.get(
            "name_abbreviation", ""
        ),

        court=data.get("court", {}).get("name", ""),
        jurisdiction=data.get(
            "jurisdiction", {}
        ).get("name_long", ""),

        decision_date=data.get(
            "decision_date", ""
        ),

        docket_number=data.get(
            "docket_number", ""
        ),

        judges=data.get(
            "casebody", {}
        ).get("judges", []),

        parties=data.get(
            "casebody", {}
        ).get("parties", []),

        attorneys=data.get(
            "casebody", {}
        ).get("attorneys", []),

        citations=citations,

        cited_cases=cited_cases,

        opinion_text=opinion_text,

        head_matter=data.get(
            "casebody", {}
        ).get("head_matter", ""),

        pagerank=pagerank,

        search_text=""

    )

    case.search_text = construct_search_text(case)

    return case
