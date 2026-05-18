from sentence_transformers import SentenceTransformer


class LegalEmbedder:

    def __init__(
        self,
        #model_name="sentence-transformers/all-MiniLM-L6-v2"
        model_name="sentence-transformers/all-mpnet-base-v2"

    ):

        self.model = SentenceTransformer(model_name)

    def embed_texts(
        self,
        texts,
        batch_size=16
    ):

        embeddings = self.model.encode(
            texts,
            batch_size=batch_size,
            show_progress_bar=True,
            convert_to_numpy=True
        )

        return embeddings

    def embed_query(self, query):

        return self.model.encode(
            [query],
            convert_to_numpy=True
        )[0]
