from sentence_transformers import (
    CrossEncoder
)


class LegalReranker:

    def __init__(
        self,
        model_name="cross-encoder/ms-marco-MiniLM-L-6-v2"
    ):

        self.model = CrossEncoder(
            model_name
        )
    def rerank(
        self,
        query,
        results
    ):

        if not results:
            return []

        pairs = [
            (query, result["chunk"].chunk_text)
            for result in results
        ]

        scores = self.model.predict(
            pairs
        )

        reranked = []

        for score, result in zip(
            scores,
            results
        ):

            reranked.append({
                "score": float(score),
                "chunk": result["chunk"],
                "summary": result.get(
                    "summary",
                    ""
                ),
                "legal_issue": result.get(
                    "legal_issue",
                    ""
                ),
                "holding": result.get(
                    "holding",
                    ""
                ),
                "procedural_posture": result.get(
                    "procedural_posture",
                    ""
                ),
                "entities": result.get(
                    "entities",
                    {}
                )
            })

        reranked.sort(
            key=lambda x: x["score"],
            reverse=True
        )

        return reranked
