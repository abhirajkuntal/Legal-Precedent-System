LEGAL_CATEGORIES = {

    "Corporate Law": [
        "fiduciary duty",
        "shareholder",
        "board of directors",
        "merger",
        "acquisition",
        "corporation",
        "securities"
    ],

    "Criminal Law": [
        "murder",
        "assault",
        "criminal",
        "sentence",
        "conviction",
        "defendant",
        "prosecution"
    ],

    "Contract Law": [
        "breach of contract",
        "agreement",
        "contract",
        "damages",
        "performance"
    ],

    "Employment Law": [
        "employment",
        "termination",
        "employee",
        "workplace",
        "discrimination"
    ],

    "Constitutional Law": [
        "constitution",
        "amendment",
        "due process",
        "equal protection",
        "constitutional"
    ],

    "Tort Law": [
        "negligence",
        "liability",
        "injury",
        "damages",
        "tort"
    ]
}


class LegalClassifier:

    def classify(
        self,
        text
    ):

        text_lower = text.lower()

        scores = {}

        for category, keywords in (
            LEGAL_CATEGORIES.items()
        ):

            score = 0

            for keyword in keywords:

                if keyword in text_lower:
                    score += 1

            scores[category] = score

        best_category = max(
            scores,
            key=scores.get
        )

        if scores[best_category] == 0:
            return "Unknown"

        return best_category
