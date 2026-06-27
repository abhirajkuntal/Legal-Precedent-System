from src.ingestion.loader import load_all_cases
from src.graph.citation_graph import CitationGraph
from src.graph.citation_resolver import CitationResolver
from src.retrieval.chunk_search import ChunkSearchEngine
from src.llm.llm_query_parser import LLMQueryParser


class LegalSearchService:

    def __init__(self):

        self.cases = load_all_cases("data/raw")

        self.resolver = CitationResolver(self.cases)

        self.citation_graph = CitationGraph(
            resolver=self.resolver
        )

        for case in self.cases:
            self.citation_graph.add_case(case)

        self.search_engine = ChunkSearchEngine(
            citation_graph=self.citation_graph
        )

        self.query_parser = LLMQueryParser()

    def get_case(self, case_id:int):
        metadata = self.search_engine.case_metadata.get(case_id)

        if metadata is None:
            return None

        return metadata


    def analyze_text(self, text: str):
        summary = self.search_engine.summarizer.summarize(text)

        analysis = self.search_engine.case_analyzer.analyze_case(
            text[:1000]
        )

        entities = self.search_engine.ner.extract_entities(
            text[:3000]
        )

        return {
            "summary": summary,
            "legal_issue": analysis.get("legal_issue", ""),
            "procedural_posture": analysis.get("procedural_posture", ""),
            "holding": analysis.get("holding", ""),
            "reasoning": analysis.get("reasoning", ""),
            "entities": entities
        }

    def search(
        self,
        query,
        court=None,
        jurisdiction=None,
        judge=None,
        category=None
    ):

        parsed = self.query_parser.parse_query(query)

        court = court or parsed.get("court")
        jurisdiction = jurisdiction or parsed.get("jurisdiction")
        judge = judge or parsed.get("judge")
        category = category or parsed.get("category")

        return self.search_engine.search(
            query=parsed["semantic_query"],
            court=court,
            jurisdiction=jurisdiction,
            judge=judge,
            category=category
        )
