import json
import time
from pathlib import Path
from statistics import mean

from app.vector_store import VectorStore


class RetrievalEvaluator:
    def __init__(
        self,
        test_file: str = "evaluation/test_questions.json",
    ):
        self.test_file = Path(test_file)
        self.vector_store = VectorStore()

    def load_questions(self) -> list[dict]:
        if not self.test_file.exists():
            raise FileNotFoundError(
                f"Evaluation file not found: {self.test_file}"
            )

        with open(self.test_file, "r", encoding="utf-8") as file:
            questions = json.load(file)

        if not isinstance(questions, list):
            raise ValueError("Evaluation file must contain a list of questions.")

        return questions

    def _normalize_source(self, value: str) -> str:
        return value.strip().lower().replace("\\", "/")

    def _is_source_match(
        self,
        retrieved_source: str,
        expected_source: str,
    ) -> bool:
        retrieved = self._normalize_source(retrieved_source)
        expected = self._normalize_source(expected_source)

        return retrieved == expected or expected in retrieved

    def _is_page_match(
        self,
        retrieved_page: int,
        expected_pages: list[int] | None,
    ) -> bool:
        if not expected_pages:
            return True

        return int(retrieved_page) in [int(page) for page in expected_pages]

    def _find_first_match_rank(
        self,
        retrieved_chunks: list[dict],
        expected_source: str,
        expected_pages: list[int] | None,
    ) -> int | None:
        for rank, chunk in enumerate(retrieved_chunks, start=1):
            source_match = self._is_source_match(
                retrieved_source=chunk["source"],
                expected_source=expected_source,
            )

            page_match = self._is_page_match(
                retrieved_page=chunk["page"],
                expected_pages=expected_pages,
            )

            if source_match and page_match:
                return rank

        return None

    def evaluate(
        self,
        top_k: int = 5,
        selected_source: str | None = None,
    ) -> dict:
        questions = self.load_questions()

        selected_source = selected_source.strip() if selected_source else None

        if selected_source in ["", "__all__", "all"]:
            selected_source = None

        results = []

        for item in questions:
            question_id = item.get("id", "")
            question = item.get("question", "").strip()

            # Nếu UI truyền selected_source thì dùng thẳng tài liệu đang chọn.
            # Nếu không có selected_source, fallback về expected_source trong JSON.
            expected_source = (
                selected_source
                or item.get("expected_source", "").strip()
            )

            expected_pages = item.get("expected_pages", [])

            if not question:
                raise ValueError(f"Question is empty in item: {item}")

            if not expected_source:
                raise ValueError(
                    "expected_source is empty. "
                    "Hãy chọn một tài liệu trên UI hoặc thêm expected_source trong test_questions.json."
                )

            start_time = time.perf_counter()

            retrieved_chunks = self.vector_store.search(
                query=question,
                top_k=top_k,
                source_filter=selected_source,
            )

            latency_ms = (time.perf_counter() - start_time) * 1000

            first_match_rank = self._find_first_match_rank(
                retrieved_chunks=retrieved_chunks,
                expected_source=expected_source,
                expected_pages=expected_pages,
            )

            hit = first_match_rank is not None
            reciprocal_rank = 1 / first_match_rank if first_match_rank else 0

            top_distance = (
                retrieved_chunks[0]["distance"]
                if retrieved_chunks
                else None
            )

            retrieved_summary = []

            for chunk in retrieved_chunks:
                retrieved_summary.append({
                    "rank": chunk["ref_id"],
                    "source": chunk["source"],
                    "page": chunk["page"],
                    "distance": chunk["distance"],
                    "preview": chunk["text"][:250],
                })

            results.append({
                "id": question_id,
                "question": question,
                "expected_source": expected_source,
                "expected_pages": expected_pages,
                "hit": hit,
                "first_match_rank": first_match_rank,
                "reciprocal_rank": reciprocal_rank,
                "latency_ms": round(latency_ms, 2),
                "top_distance": top_distance,
                "retrieved": retrieved_summary,
            })

        total = len(results)

        hit_count = sum(1 for item in results if item["hit"])
        reciprocal_ranks = [item["reciprocal_rank"] for item in results]
        latencies = [item["latency_ms"] for item in results]

        valid_top_distances = [
            item["top_distance"]
            for item in results
            if item["top_distance"] is not None
        ]

        metrics = {
            "selected_source": selected_source,
            "total_questions": total,
            "top_k": top_k,
            "hit_count": hit_count,
            "hit_at_k": round(hit_count / total, 4) if total else 0,
            "mrr": round(mean(reciprocal_ranks), 4) if reciprocal_ranks else 0,
            "avg_latency_ms": round(mean(latencies), 2) if latencies else 0,
            "avg_top_distance": (
                round(mean(valid_top_distances), 4)
                if valid_top_distances
                else None
            ),
        }

        return {
            "metrics": metrics,
            "results": results,
        }