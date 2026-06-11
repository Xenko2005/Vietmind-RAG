import os
import requests


class OllamaClient:
    def __init__(
        self,
        model: str = "qwen3:4b",
        base_url: str | None = None,
    ):
        self.model = model
        self.base_url = base_url or os.getenv(
            "OLLAMA_BASE_URL",
            "http://localhost:11434",
        )

    def chat(self, prompt: str) -> str:
        url = f"{self.base_url}/api/chat"

        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "Bạn là trợ lý AI tiếng Việt cho hệ thống RAG. "
                        "Chỉ trả lời dựa trên CONTEXT được cung cấp. "
                        "Nếu không có đủ thông tin trong CONTEXT, hãy nói rõ là tài liệu hiện có chưa cung cấp đủ thông tin. "
                        "Không bịa nguồn, không bịa tên file, không bịa số trang."
                    ),
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            "stream": False,
        }

        response = requests.post(
            url,
            json=payload,
            timeout=180,
        )

        response.raise_for_status()

        data = response.json()
        return data["message"]["content"]