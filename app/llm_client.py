import requests


class OllamaClient:
    def __init__(
        self,
        model: str = "qwen3:4b",
        base_url: str = "http://localhost:11434"
    ):
        self.model = model
        self.base_url = base_url

    def chat(self, prompt: str) -> str:
        url = f"{self.base_url}/api/chat"

        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "Bạn là trợ lý AI tiếng Việt. "
                        "Chỉ trả lời dựa trên CONTEXT được cung cấp. "
                        "Nếu không tìm thấy thông tin trong CONTEXT, hãy nói rõ là không có đủ thông tin. "
                        "Không bịa nguồn."
                    )
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "stream": False
        }

        response = requests.post(url, json=payload, timeout=120)
        response.raise_for_status()

        data = response.json()
        return data["message"]["content"]