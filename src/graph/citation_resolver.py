class CitationResolver:

    def __init__(self, cases):

        self.citation_map = {}

        self.build_map(cases)

    def build_map(self, cases):

        for case in cases:

            for citation in case.citations:

                cleaned = citation.strip()

                self.citation_map[
                    cleaned
                ] = case.case_id

    def resolve(self, citation_text):

        if not citation_text:
            return None

        cleaned = citation_text.strip()

        return self.citation_map.get(cleaned)
