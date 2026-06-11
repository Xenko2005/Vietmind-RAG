import chromadb
from app.embedder import E5Embedder


class VectorStore:
    def __init__(
        self,
        persist_dir: str = "data/chroma_db",
        collection_name: str = "vietmind_docs"
    ):
        self.client = chromadb.PersistentClient(path=persist_dir)
        self.collection = self.client.get_or_create_collection(
            name=collection_name
        )
        self.embedder = E5Embedder()

    def add_chunks(self, chunks: list[dict]) -> int:
        if not chunks:
            return 0

        texts = [chunk["text"] for chunk in chunks]
        embeddings = self.embedder.embed_documents(texts)

        ids = []
        metadatas = []

        for idx, chunk in enumerate(chunks):
            doc_id = f'{chunk["source"]}_p{chunk["page"]}_c{chunk["chunk_id"]}_{idx}'
            ids.append(doc_id)

            metadatas.append({
                "source": chunk["source"],
                "page": chunk["page"],
                "chunk_id": chunk["chunk_id"]
            })

        self.collection.add(
            ids=ids,
            documents=texts,
            embeddings=embeddings,
            metadatas=metadatas
        )

        return len(chunks)

    def search(self, query: str, top_k: int = 5) -> list[dict]:
        query_embedding = self.embedder.embed_query(query)

        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k
        )

        retrieved = []

        docs = results.get("documents", [[]])[0]
        metas = results.get("metadatas", [[]])[0]
        distances = results.get("distances", [[]])[0]

        for doc, meta, distance in zip(docs, metas, distances):
            retrieved.append({
                "text": doc,
                "source": meta["source"],
                "page": meta["page"],
                "chunk_id": meta["chunk_id"],
                "distance": distance
            })

        return retrieved