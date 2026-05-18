from collections import defaultdict


class CitationGraph:

    def __init__(self, resolver=None):

        self.graph = defaultdict(set)

        self.reverse_graph = defaultdict(set)

        self.resolver = resolver

    def add_case(self, case):

        source_id = case.case_id

        for cited in case.cited_cases:

            target_id = None

            if self.resolver:

                target_id = (
                    self.resolver.resolve(cited)
                )

            if not target_id:
                continue

            self.graph[source_id].add(
                target_id
            )

            self.reverse_graph[target_id].add(
                source_id
            )

    def get_cited_cases(self, case_id):

        return list(
            self.graph.get(case_id, [])
        )

    def get_citing_cases(self, case_id):

        return list(
            self.reverse_graph.get(case_id, [])
        )

    def citation_count(self, case_id):

        return len(
            self.reverse_graph.get(case_id, [])
        )
