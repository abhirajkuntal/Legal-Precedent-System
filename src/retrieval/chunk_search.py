from src.artifacts.artifact_builder import ArtifactBuilder

from src.preprocessing.chunker import (
    split_into_chunks
)

from src.llm.legal_case_analyzer import (
    LegalCaseAnalyzer
)

from src.llm.legal_answer_synthesizer import (
    LegalAnswerSynthesizer
)


from src.embedding.embedder import (
    LegalEmbedder
)

from src.summarization.legal_summarizer import (
        LegalSummarizer
)

from src.retrieval.reranker import (
        LegalReranker
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

from src.indexing.faiss_index import (
    FaissIndexer
)
from pathlib import Path

from src.indexing.storage import (
    save_chunks,
    load_chunks,
    save_embeddings,
    load_embeddings,
    save_faiss_index,
    load_faiss_index
)

class ChunkSearchEngine:

    def __init__(self, cases, citation_graph=None):

        self.cases = cases
        self.citation_graph = citation_graph
        self.case_analyzer = LegalCaseAnalyzer()
        self.answer_synthesizer = LegalAnswerSynthesizer()

        self.case_lookup = {
            case.case_id: case
            for case in cases}


        self.embedder = LegalEmbedder()

        chunks_path = "data/processed/chunks.pkl"

        embeddings_path = (
            "data/embeddings/chunk_embeddings.npy"
        )

        index_path = (
            "data/indexes/chunk_faiss.index"
        )

        if (
            Path(chunks_path).exists()
            and Path(embeddings_path).exists()
            and Path(index_path).exists()
        ):

            print("Loading saved data...")

            self.chunks = load_chunks(
                chunks_path
            )

            self.embeddings = load_embeddings(
                embeddings_path
            )

            faiss_index = load_faiss_index(
                index_path
            )

            embedding_dim = (
                self.embeddings.shape[1]
            )

            self.index = FaissIndexer(
                embedding_dim
            )

            self.index.load_existing_index(
                faiss_index
            )

        else:
            builder = ArtifactBuilder()

            self.chunks = builder.build_chunks(cases)

            chunk_texts = [
                chunk.chunk_text
                for chunk in self.chunks
            ]

            print(
                "Generating chunk embeddings..."
            )

            self.chunks = builder.build_chunks(cases)
            self.embeddings = builder.build_embeddings(self.chunks)
            self.index = builder.build_faiss(self.embeddings)

            builder.save(self.chunks, self.embeddings, self.index)

        print("Building BM25 index...")

        self.bm25_index = BM25Search(
            self.chunks
        )

        print("Loading reranker...")
    
        self.reranker = LegalReranker()
        
        print("Loading summarizer...")

        self.summarizer = LegalSummarizer()

        print("Loading legal extractor...")

        self.extractor = LegalExtractor()

        print("Loading legal NER...")

        self.ner = LegalNER()

        self.reranker = LegalCrossEncoder()

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

        filtered_indices = [
            self.chunks.index(chunk)
            for chunk in filtered_chunks
        ]

        filtered_embeddings = self.embeddings[
            filtered_indices
        ]

        temp_index = FaissIndexer(
            self.embeddings.shape[1]
        )

        temp_index.add_embeddings(
            filtered_embeddings
        )

        query_embedding = self.embedder.embed_query(
            query
        )

        semantic_distances, semantic_indices = (
            temp_index.search(
                query_embedding,
                top_k=initial_k
            )
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

        for result in reranked_results[:top_k]:

            chunk = result["chunk"]

            full_case = self.case_lookup[
                chunk.case_id
            ]

            full_text = f"""
            {full_case.title}

            Court: {full_case.court}

            Jurisdiction: {full_case.jurisdiction}

            Judges: {' '.join(full_case.judges)}

            Head Matter:
            {full_case.head_matter}

            Opinion:
            {full_case.opinion_text}
            """

            summary = self.summarizer.summarize(
                chunk.chunk_text
            )

            entities = self.ner.extract_entities(
                full_text[:3000]
            )

            analysis = (
                self.case_analyzer.analyze_case(
                    chunk.chunk_text[:1000]
                )
            )

            final_results.append({
                "score": result["score"],
                "chunk": chunk,
                "summary": summary,
                "legal_issue":
                    analysis.get(
                        "legal_issue",
                        ""
                    ),

                "procedural_posture":
                    analysis.get(
                        "procedural_posture",
                        ""
                    ),

                "holding":
                    analysis.get(
                        "holding",
                        ""
                    ),

                "reasoning":
                    analysis.get(
                        "reasoning",
                        ""
                    ),

                "entities": entities,

                "citation_score":
                    result.get(
                        "citation_score",
                        0
                    ),

                "rerank_score":
                    result.get(
                        "rerank_score",
                        0
                    )
            })

        #synthesized_answer = (self.answer_synthesizer.synthesize(query,final_results))
        

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
