from sentence_transformers import SentenceTransformer


class E5Embedder:
    def __init__(self, model_name: str = "intfloat/multilingual-e5-small"):
        self.model = SentenceTransformer(model_name)

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        inputs = [f"passage: {text}" for text in texts]

        embeddings = self.model.encode(
            inputs,
            normalize_embeddings=True,
            convert_to_numpy=True,
        )

        return embeddings.tolist()

    def embed_query(self, query: str) -> list[float]:
        embedding = self.model.encode(
            f"query: {query}",
            normalize_embeddings=True,
            convert_to_numpy=True,
        )

        return embedding.tolist()