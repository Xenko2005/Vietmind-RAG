import re

from app.vector_store import VectorStore
from app.llm_client import OllamaClient


class RAGPipeline:
    def __init__(self, llm_model: str = "qwen3:4b"):
        self.vector_store = VectorStore()
        self.llm = OllamaClient(model=llm_model)

    def _remove_think_tags(self, text: str) -> str:
        cleaned = re.sub(
            r"<think>.*?</think>",
            "",
            text,
            flags=re.DOTALL | re.IGNORECASE,
        )

        return cleaned.strip()

    def build_context(self, chunks: list[dict]) -> str:
        context_parts = []

        for chunk in chunks:
            context_parts.append(
                f"[Nguồn {chunk['ref_id']}]\n"
                f"File: {chunk['source']}\n"
                f"Trang: {chunk['page']}\n"
                f"Nội dung:\n{chunk['text']}"
            )

        return "\n\n---\n\n".join(context_parts)

    def build_sources_text(self, chunks: list[dict]) -> str:
        if not chunks:
            return "Không có nguồn truy xuất."

        lines = []
        used = set()

        for chunk in chunks:
            key = (chunk["source"], chunk["page"])

            if key in used:
                continue

            used.add(key)

            lines.append(
                f"- [Nguồn {chunk['ref_id']}] "
                f"{chunk['source']} — trang {chunk['page']}"
            )

        return "\n".join(lines)

    def ask(self, question: str, top_k: int = 5) -> dict:
        retrieved_chunks = self.vector_store.search(
            query=question,
            top_k=top_k,
        )

        if not retrieved_chunks:
            return {
                "answer": "Mình chưa tìm thấy tài liệu liên quan trong knowledge base.",
                "sources_text": "Không có nguồn truy xuất.",
                "sources": [],
            }

        context = self.build_context(retrieved_chunks)

        prompt = f"""
Bạn là trợ lý AI tiếng Việt cho hệ thống VietMind-RAG.

NHIỆM VỤ:
Trả lời câu hỏi của người dùng dựa trên CONTEXT được cung cấp.

QUY TẮC BẮT BUỘC:
1. Chỉ dùng thông tin có trong CONTEXT.
2. Nếu CONTEXT không đủ thông tin, hãy nói rõ: "Tài liệu hiện có chưa cung cấp đủ thông tin để trả lời chính xác."
3. Không bịa thông tin.
4. Không bịa tên file, số trang hoặc nguồn.
5. Khi dùng thông tin từ đoạn nào, hãy ghi kèm mã nguồn dạng [Nguồn 1], [Nguồn 2].
6. Trả lời tự nhiên, dễ hiểu, bằng tiếng Việt.

CONTEXT:
{context}

CÂU HỎI:
{question}

CÂU TRẢ LỜI:
"""

        answer = self.llm.chat(prompt)
        answer = self._remove_think_tags(answer)

        sources_text = self.build_sources_text(retrieved_chunks)

        final_answer = f"""{answer}

---

**Nguồn truy xuất:**

{sources_text}
"""

        return {
            "answer": final_answer,
            "sources_text": sources_text,
            "sources": retrieved_chunks,
        }