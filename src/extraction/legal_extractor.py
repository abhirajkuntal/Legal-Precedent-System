import re


class LegalExtractor:

    def extract_legal_issue(
        self,
        text
    ):

        patterns = [
            r"issue[s]?\s+(before|presented).*?\.",
            r"whether .*?\.",
            r"the question is .*?\."
        ]

        for pattern in patterns:

            match = re.search(
                pattern,
                text,
                re.IGNORECASE
            )

            if match:
                return match.group(0)

        return ""

    def extract_holding(
        self,
        text
    ):

        patterns = [
            r"we hold that .*?\.",
            r"the court holds .*?\.",
            r"we conclude that .*?\."
        ]

        for pattern in patterns:

            match = re.search(
                pattern,
                text,
                re.IGNORECASE
            )

            if match:
                return match.group(0)

        return ""

    def extract_procedural_posture(
        self,
        text
    ):

        patterns = [
            r"appeal from .*?\.",
            r"on appeal .*?\.",
            r"plaintiff brought .*?\."
        ]

        for pattern in patterns:

            match = re.search(
                pattern,
                text,
                re.IGNORECASE
            )

            if match:
                return match.group(0)

        return ""
