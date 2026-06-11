from app.vector_store import VectorStore
from app.llm_client import OllamaClient


class RAGPipeline:
    def __init__(self):
        self.vector_store = VectorStore()
        self.llm = OllamaClient()

    def build_context(self, chunks: list[dict]) -> str:
        context_parts = []

        for idx, chunk in enumerate(chunks, start=1):
            context_parts.append(
                f"[Nguồn {idx}] File: {chunk['source']} | Trang: {chunk['page']}\n"
                f"{chunk['text']}"
            )

        return "\n\n".join(context_parts)

    def ask(self, question: str, top_k: int = 5) -> dict:
        retrieved_chunks = self.vector_store.search(question, top_k=top_k)
        context = self.build_context(retrieved_chunks)

        prompt = f"""
CONTEXT:
{context}

QUESTION:
{question}

YÊU CẦU TRẢ LỜI:
- Trả lời bằng tiếng Việt.
- Chỉ dùng thông tin trong CONTEXT.
- Cuối câu trả lời, ghi phần "Nguồn tham khảo".
- Nguồn tham khảo cần ghi tên file và trang.
"""

        answer = self.llm.chat(prompt)

        return {
            "answer": answer,
            "sources": retrieved_chunks
        }