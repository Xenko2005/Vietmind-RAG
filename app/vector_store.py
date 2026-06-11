import hashlib
import chromadb

from app.embedder import E5Embedder


class VectorStore:
    def __init__(
        self,
        persist_dir: str = "data/chroma_db",
        collection_name: str = "vietmind_docs",
    ):
        self.persist_dir = persist_dir
        self.collection_name = collection_name

        self.client = chromadb.PersistentClient(path=persist_dir)
        self.collection = self.client.get_or_create_collection(
            name=collection_name
        )

        self.embedder = E5Embedder()

    def _make_chunk_id(self, chunk: dict) -> str:
        raw_id = (
            f"{chunk['source']}|"
            f"{chunk['page']}|"
            f"{chunk['chunk_id']}|"
            f"{chunk['text'][:100]}"
        )

        return hashlib.md5(raw_id.encode("utf-8")).hexdigest()

    def delete_by_source(self, source: str) -> int:
        results = self.collection.get(
            include=["metadatas"]
        )

        ids = results.get("ids", [])
        metadatas = results.get("metadatas", [])

        ids_to_delete = []

        for item_id, meta in zip(ids, metadatas):
            if meta and meta.get("source") == source:
                ids_to_delete.append(item_id)

        if ids_to_delete:
            self.collection.delete(ids=ids_to_delete)

        return len(ids_to_delete)

    def add_chunks(
        self,
        chunks: list[dict],
        replace_existing: bool = True,
    ) -> int:
        if not chunks:
            return 0

        source = chunks[0]["source"]

        if replace_existing:
            self.delete_by_source(source)

        texts = [chunk["text"] for chunk in chunks]
        embeddings = self.embedder.embed_documents(texts)

        ids = []
        metadatas = []

        for chunk in chunks:
            ids.append(self._make_chunk_id(chunk))

            metadatas.append({
                "source": chunk["source"],
                "page": chunk["page"],
                "chunk_id": chunk["chunk_id"],
            })

        self.collection.upsert(
            ids=ids,
            documents=texts,
            embeddings=embeddings,
            metadatas=metadatas,
        )

        return len(chunks)

    def search(self, query: str, top_k: int = 5) -> list[dict]:
        query_embedding = self.embedder.embed_query(query)

        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
        )

        retrieved = []

        docs = results.get("documents", [[]])[0]
        metas = results.get("metadatas", [[]])[0]
        distances = results.get("distances", [[]])[0]

        for idx, (doc, meta, distance) in enumerate(
            zip(docs, metas, distances),
            start=1,
        ):
            retrieved.append({
                "ref_id": idx,
                "text": doc,
                "source": meta["source"],
                "page": meta["page"],
                "chunk_id": meta["chunk_id"],
                "distance": float(distance),
            })

        return retrieved

    def list_documents(self) -> list[dict]:
        results = self.collection.get(
            include=["metadatas"]
        )

        metadatas = results.get("metadatas", [])

        docs = {}

        for meta in metadatas:
            if not meta:
                continue

            source = meta["source"]
            page = meta["page"]

            if source not in docs:
                docs[source] = {
                    "source": source,
                    "num_chunks": 0,
                    "pages": set(),
                }

            docs[source]["num_chunks"] += 1
            docs[source]["pages"].add(page)

        output = []

        for source, info in docs.items():
            pages = sorted(list(info["pages"]))

            output.append({
                "source": source,
                "num_chunks": info["num_chunks"],
                "num_pages": len(pages),
                "pages": pages,
            })

        return sorted(output, key=lambda item: item["source"])

    def count_chunks(self) -> int:
        return self.collection.count()

    def reset(self) -> None:
        try:
            self.client.delete_collection(name=self.collection_name)
        except Exception:
            pass

        self.collection = self.client.get_or_create_collection(
            name=self.collection_name
        )