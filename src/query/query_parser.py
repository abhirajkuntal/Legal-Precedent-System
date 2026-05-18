import re


KNOWN_COURTS = [
    "Delaware Court of Chancery",
    "Delaware Supreme Court"
]


KNOWN_JURISDICTIONS = [
    "Delaware",
    "Michigan"
]


def extract_court(query):

    patterns = [
        r'from (.+?) court',
        r'in (.+?) court'
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            query,
            re.IGNORECASE
        )

        if match:

            extracted = (
                match.group(1).strip()
            )

            for court in KNOWN_COURTS:

                if extracted.lower() in court.lower():
                    return court

    for court in KNOWN_COURTS:

        if court.lower() in query.lower():
            return court

    return None

def extract_jurisdiction(query):

    patterns = [
        r'from ([A-Za-z]+)',
        r'in ([A-Za-z]+)'
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            query,
            re.IGNORECASE
        )

        if match:

            extracted = (
                match.group(1).strip()
            )

            for jurisdiction in KNOWN_JURISDICTIONS:

                if (
                    extracted.lower()
                    == jurisdiction.lower()
                ):
                    return jurisdiction

    for jurisdiction in KNOWN_JURISDICTIONS:

        if jurisdiction.lower() in query.lower():
            return jurisdiction

    return None

def extract_judge(query):

    patterns = [
            r"judge\s+([A-Za-z ]+?)(?:\s+from|\s+in|$)"
            r"justice\s+([A-Za-z ]+?)(?:\s+from|\s+in|$)"
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            query,
            re.IGNORECASE
        )

        if match:

            return (
                match.group(1)
                .strip()
            )

    return None

def clean_semantic_query(
    query,
    court,
    jurisdiction,
    judge
):

    cleaned = query

    removable_items = [
        court,
        jurisdiction
    ]

    if judge:
        removable_items.extend([
            f"judge {judge}",
            f"justice {judge}"
        ])

    for item in removable_items:

        if item:
            cleaned = re.sub(
                re.escape(item),
                "",
                cleaned,
                flags=re.IGNORECASE
            )

    cleaned = re.sub(
        r"\s+",
        " ",
        cleaned
    ).strip()

    return cleaned


def parse_query(query):

    court = extract_court(query)

    jurisdiction = extract_jurisdiction(query)

    judge = extract_judge(query)

    semantic_query = clean_semantic_query(
        query,
        court,
        jurisdiction,
        judge
    )

    return {
        "semantic_query": semantic_query,
        "court": court,
        "jurisdiction": jurisdiction,
        "judge": judge
    }
