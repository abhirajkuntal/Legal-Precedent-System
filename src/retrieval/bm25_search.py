from rank_bm25 import BM25Okapi


class BM25Search:

    def __init__(self, chunks):

        self.chunks = chunks

        self.corpus = [
            chunk.chunk_text.split()
            for chunk in chunks
        ]

        self.bm25 = BM25Okapi(self.corpus)

    def search(
        self,
        query,
        top_k=10
    ):

        tokenized_query = query.split()

        scores = self.bm25.get_scores(
            tokenized_query
        )

        ranked_indices = sorted(
            range(len(scores)),
            key=lambda i: scores[i],
            reverse=True
        )

        results = []

        for idx in ranked_indices[:top_k]:

            results.append({
                "score": float(scores[idx]),
                "chunk": self.chunks[idx]
            })

        return results
