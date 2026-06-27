from src.artifacts.artifact_loader import ArtifactLoader

from src.embedding.embedder import LegalEmbedder
from src.retrieval.bm25_search import BM25Search
from src.reranking.cross_encoder import LegalCrossEncoder

from src.summarization.legal_summarizer import LegalSummarizer
from src.extraction.legal_ner import LegalNER
from src.llm.legal_case_analyzer import LegalCaseAnalyzer


class ChunkSearchEngine:

    def __init__(self, citation_graph=None):

        # =========================
        # LOAD ARTIFACTS
        # =========================
        loader = ArtifactLoader()
        artifacts = loader.load()

        self.index = artifacts["index"]
        self.case_metadata = artifacts["case_metadata"]

        # IMPORTANT: chunks should ideally be metadata-only or lightweight
        self.chunks = artifacts.get("chunks", [])

        # =========================
        # OPTIONAL GRAPH
        # =========================
        self.citation_graph = citation_graph

        # =========================
        # INDEXES
        # =========================
        self.bm25_index = BM25Search(self.chunks)

        # =========================
        # MODELS
        # =========================
        self.embedder = LegalEmbedder()
        self.reranker = LegalCrossEncoder()

        self.summarizer = LegalSummarizer()
        self.ner = LegalNER()
        self.case_analyzer = LegalCaseAnalyzer()

        # =========================
        # LOOKUP MAP (FAST ACCESS)
        # =========================
        self.chunk_id_to_chunk = {
            chunk.chunk_id: chunk
            for chunk in self.chunks
        }

    # =========================
    # CITATION SCORE
    # =========================
    def get_citation_score(self, case_id):
        if not self.citation_graph:
            return 0

        count = self.citation_graph.citation_count(case_id)
        return min(count / 10, 1.0)

    # =========================
    # SEARCH
    # =========================
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

        # -------------------------
        # FILTER (LIGHTWEIGHT)
        # -------------------------
        filtered_chunks = self.filter_chunks(
            court=court,
            jurisdiction=jurisdiction,
            judge=judge,
            category=category
        )

        if not filtered_chunks:
            return {"results": []}

        filtered_ids = {c.chunk_id for c in filtered_chunks}

        # -------------------------
        # SEMANTIC SEARCH (GLOBAL INDEX)
        # -------------------------
        query_embedding = self.embedder.embed_query(query)

        distances, indices = self.index.search(
            query_embedding,
            top_k=initial_k
        )

        semantic_scores = {}

        for dist, idx in zip(distances, indices):

            # IMPORTANT: FAISS is global index → must map safely
            chunk = self.chunks[idx]

            if chunk.chunk_id not in filtered_ids:
                continue

            semantic_scores[chunk.chunk_id] = 1 / (1 + float(dist))

        # -------------------------
        # BM25 SEARCH
        # -------------------------
        bm25_results = self.bm25_index.search(query, top_k=initial_k)

        bm25_scores = {}

        for r in bm25_results:
            chunk = r["chunk"]

            if chunk.chunk_id not in filtered_ids:
                continue

            bm25_scores[chunk.chunk_id] = r["score"]

        # -------------------------
        # COMBINE SCORES
        # -------------------------
        combined = []

        for chunk in filtered_chunks:

            s_score = semantic_scores.get(chunk.chunk_id, 0)
            b_score = bm25_scores.get(chunk.chunk_id, 0)

            citation_score = self.get_citation_score(chunk.case_id)

            metadata_score = 0

            if court and chunk.court and court.lower() in chunk.court.lower():
                metadata_score += 0.3

            if jurisdiction and chunk.jurisdiction and jurisdiction.lower() in chunk.jurisdiction.lower():
                metadata_score += 0.2

            if judge:
                if any(judge.lower() in j.lower() for j in chunk.judges):
                    metadata_score += 0.4

            if category and chunk.legal_category and category.lower() in chunk.legal_category.lower():
                metadata_score += 0.3

            pagerank_boost = getattr(chunk, "pagerank", 0) * 0.1

            score = (
                0.55 * s_score +
                0.20 * b_score +
                0.15 * citation_score +
                metadata_score +
                pagerank_boost
            )

            if score < 2:
                continue

            combined.append({
                "score": score,
                "chunk": chunk,
                "citation_score": citation_score
            })

        combined.sort(key=lambda x: x["score"], reverse=True)

        # -------------------------
        # DEDUP CASES
        # -------------------------
        seen_cases = set()
        unique = []

        for item in combined:

            chunk = item["chunk"]

            if chunk.case_id in seen_cases:
                continue

            seen_cases.add(chunk.case_id)

            unique.append(item)

            if len(unique) >= top_k:
                break

        # -------------------------
        # RERANK
        # -------------------------
        reranked = self.reranker.rerank(query, unique)

        # -------------------------
        # FINAL OUTPUT
        # -------------------------
        results = []

        for r in reranked[:top_k]:

            chunk = r["chunk"]

            meta = self.case_metadata.get(chunk.case_id)

            if not meta:
                continue

            summary = self.summarizer.summarize(chunk.chunk_text)

            entities = self.ner.extract_entities(chunk.chunk_text[:3000])

            analysis = self.case_analyzer.analyze_case(chunk.chunk_text[:1000])

            results.append({
                "score": r["score"],
                "chunk": chunk,

                "case_metadata": {
                    "case_id": meta.case_id,
                    "title": meta.title,
                    "court": meta.court,
                    "jurisdiction": meta.jurisdiction,
                    "judges": meta.judges,
                    "pagerank": getattr(meta, "pagerank", 0)
                },

                "summary": summary,
                "legal_issue": analysis.get("legal_issue", ""),
                "procedural_posture": analysis.get("procedural_posture", ""),
                "holding": analysis.get("holding", ""),
                "reasoning": analysis.get("reasoning", ""),

                "entities": entities,
                "citation_score": r.get("citation_score", 0),
                "rerank_score": r.get("rerank_score", 0)
            })

        return {"results": results}

    # =========================
    # FILTERING
    # =========================
    def filter_chunks(
        self,
        court=None,
        jurisdiction=None,
        judge=None,
        category=None
    ):

        chunks = self.chunks

        if court:
            chunks = [c for c in chunks if c.court and court.lower() in c.court.lower()]

        if jurisdiction:
            chunks = [c for c in chunks if c.jurisdiction and jurisdiction.lower() in c.jurisdiction.lower()]

        if judge:
            chunks = [
                c for c in chunks
                if any(judge.lower() in j.lower() for j in c.judges)
            ]

        if category:
            chunks = [
                c for c in chunks
                if c.legal_category and category.lower() in c.legal_category.lower()
            ]

        return chunks
