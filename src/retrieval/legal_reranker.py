from sentence_transformers import CrossEncoder


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

        pairs = []

        for result in results:

            chunk = result["chunk"]

            pairs.append([
                query,
                chunk.chunk_text
            ])

        scores = self.model.predict(
            pairs
        )

        reranked = []

        for score, result in zip(
            scores,
            results
        ):

            result["rerank_score"] = float(score)

            reranked.append(result)

        reranked.sort(
            key=lambda x: x["rerank_score"],
            reverse=True
        )

        return reranked
