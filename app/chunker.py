def chunk_text(
    pages: list[dict],
    chunk_size: int = 800,
    overlap: int = 150
) -> list[dict]:
    chunks = []

    for page in pages:
        text = page["text"]
        start = 0
        chunk_id = 0

        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end].strip()

            if chunk:
                chunks.append({
                    "text": chunk,
                    "source": page["source"],
                    "page": page["page"],
                    "chunk_id": chunk_id
                })

            start += chunk_size - overlap
            chunk_id += 1

    return chunks