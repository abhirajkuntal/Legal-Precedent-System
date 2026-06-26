from src.llm.legal_case_analyzer import (
    LegalCaseAnalyzer
)

from src.embedding.embedder import LegalEmbedder

from src.llm.legal_answer_synthesizer import (
    LegalAnswerSynthesizer
)


from src.summarization.legal_summarizer import (
        LegalSummarizer
)


from src.retrieval.bm25_search import (
        BM25Search
)

from src.extraction.legal_extractor import (
        LegalExtractor
)

from src.reranking.cross_encoder import (
        LegalCrossEncoder
)

from src.extraction.legal_ner import (
    LegalNER
)


from src.artifacts.artifact_loader import ArtifactLoader
from src.retrieval.bm25_search import BM25Search
from src.reranking.cross_encoder import LegalCrossEncoder

from src.llm.legal_case_analyzer import LegalCaseAnalyzer
from src.llm.legal_answer_synthesizer import LegalAnswerSynthesizer

from src.summarization.legal_summarizer import LegalSummarizer
from src.extraction.legal_extractor import LegalExtractor
from src.extraction.legal_ner import LegalNER


class ChunkSearchEngine:

    def __init__(self, citation_graph=None):

        # =========================
        # ONLINE ARTIFACT LOADING
        # =========================
        loader = ArtifactLoader()
        artifacts = loader.load()

        self.chunks = artifacts["chunks"]
        self.embeddings = artifacts["embeddings"]
        self.index = artifacts["index"]

        # =========================
        # GRAPH (optional)
        # =========================
        self.citation_graph = citation_graph

        # =========================
        # LOOKUP TABLE (for now)
        # =========================
        self.case_lookup = {
            chunk.case_id: chunk
            for chunk in self.chunks
        }

        # =========================
        # SEARCH COMPONENTS
        # =========================
        self.bm25_index = BM25Search(self.chunks)

        # =========================
        # LLM / NLP COMPONENTS
        # =========================
        self.case_analyzer = LegalCaseAnalyzer()
        self.answer_synthesizer = LegalAnswerSynthesizer()

        self.summarizer = LegalSummarizer()
        self.extractor = LegalExtractor()
        self.ner = LegalNER()

        self.reranker = LegalCrossEncoder()

        self.embedder = LegalEmbedder()

    def get_citation_score(self,case_id):
        
        if not self.citation_graph:
            return 0

        citation_count = (
                self.citation_graph.citation_count(case_id)
                )
        return min(citation_count / 10, 1.0)

    def search(
        self,
        query,
        top_k=5,
        initial_k=20,
        court=None,
        jurisdiction=None,
        judge=None,
        category=None
    ):

        filtered_chunks = self.filter_chunks(
            court=court,
            jurisdiction=jurisdiction,
            judge=judge
        )

        if not filtered_chunks:
            return []

        query_embedding = self.embedder.embed_query(query)

        semantic_distances, semantic_indices = self.index.search(
                query_embedding,
                top_k=initial_k
                )


        semantic_scores = {}

        for distance, idx in zip(
            semantic_distances,
            semantic_indices
        ):

            chunk = filtered_chunks[idx]

            semantic_scores[
                chunk.chunk_id
            ] = 1 / (1 + float(distance))

        bm25_results = self.bm25_index.search(
            query,
            top_k=initial_k
        )

        bm25_scores = {}

        for result in bm25_results:

            chunk = result["chunk"]

            if chunk not in filtered_chunks:
                continue

            bm25_scores[
                chunk.chunk_id
            ] = result["score"]

        combined_results = []

        for chunk in filtered_chunks:

            semantic_score = semantic_scores.get(
                chunk.chunk_id,
                0
            )

            bm25_score = bm25_scores.get(
                chunk.chunk_id,
                0
            )

            citation_score = self.get_citation_score(
                chunk.case_id
            )
            
            
            metadata_score = 0

            if court:
                if chunk.court and (
                    court.lower()
                    in chunk.court.lower()
                ):
                    metadata_score += 0.3

            if jurisdiction:
                if chunk.jurisdiction and (
                    jurisdiction.lower()
                    in chunk.jurisdiction.lower()
                ):
                    metadata_score += 0.2

            if judge:

                judges_text = " ".join(
                    chunk.judges
                ).lower()

                if judge.lower() in judges_text:
                    metadata_score += 0.4
            if category:
                if chunk.legal_category and (
                    category.lower()
                    in chunk.legal_category.lower()
                ):
                    metadata_score += 0.3


            pagerank_boost = (
                chunk.pagerank * 0.1
            )

            combined_score = (
                0.55 * semantic_score
                + 0.20 * bm25_score
                + 0.15 * citation_score
                + metadata_score
                + pagerank_boost
            )

            MIN_SCORE_THRESHOLD = 2

            if combined_score < MIN_SCORE_THRESHOLD:

                continue

            combined_results.append({
                "score": combined_score,
                "chunk": chunk
            })

        combined_results.sort(
            key=lambda x: x["score"],
            reverse=True
        )

        seen_cases = set()

        unique_results = []

        for result in combined_results:

            chunk = result["chunk"]

            if chunk.case_id in seen_cases:
                continue

            seen_cases.add(chunk.case_id)

            summary = self.summarizer.summarize(
                chunk.chunk_text
            )

            unique_results.append({
                "score": result["score"],
                "chunk": chunk,
                "citation_score": self.get_citation_score(chunk.case_id)
                })

            if len(unique_results) >= top_k:
                break

        reranked_results = self.reranker.rerank(
            query,
            unique_results
        )

        final_results = []

        #TODO: Using chunk text to get data and not whole case, might need to change some bit here 

        for result in reranked_results[:top_k]:


            chunk = result["chunk"]
            summary = self.summarizer.summarize(
                chunk.chunk_text
            )

            entities = self.ner.extract_entities(
                chunk.chunk_text[:3000]
            )

            analysis = self.case_analyzer.analyze_case(
                chunk.chunk_text[:1000]
            )

            final_results.append({
                "score": result["score"],
                "chunk": chunk,
                "summary": summary,

                "legal_issue": analysis.get("legal_issue", ""),
                "procedural_posture": analysis.get("procedural_posture", ""),
                "holding": analysis.get("holding", ""),
                "reasoning": analysis.get("reasoning", ""),

                "entities": entities,

                "citation_score": result.get("citation_score", 0),
                "rerank_score": result.get("rerank_score", 0)
            }) 

        return {"results":final_results,
                #"answer": synthesized_answer
                }

    def filter_chunks(
        self,
        court=None,
        jurisdiction=None,
        judge=None,
        category=None
    ):

        filtered_chunks = self.chunks

        if court:

            filtered_chunks = [
                chunk
                for chunk in filtered_chunks
                if court.lower()
                in chunk.court.lower()
            ]

        if jurisdiction:

            filtered_chunks = [
                chunk
                for chunk in filtered_chunks
                if jurisdiction.lower()
                in chunk.jurisdiction.lower()
            ]

        if judge:

            filtered_chunks = [
                chunk
                for chunk in filtered_chunks
                if any(
                    judge.lower() in j.lower()
                    for j in chunk.judges
                )
            ]

        if category:
            
            filtered_chunks = [
                chunk
                for chunk in filtered_chunks
                if (chunk.legal_category and category.lower()
                in chunk.legal_category.lower()
                    )
            ]

        return filtered_chunks
