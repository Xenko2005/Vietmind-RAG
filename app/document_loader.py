import os
import fitz
from docx import Document


def load_pdf(file_path: str) -> list[dict]:
    pages = []
    doc = fitz.open(file_path)

    for page_idx, page in enumerate(doc):
        text = page.get_text("text").strip()

        if text:
            pages.append({
                "text": text,
                "page": page_idx + 1,
                "source": os.path.basename(file_path),
            })

    doc.close()
    return pages


def load_txt(file_path: str) -> list[dict]:
    with open(file_path, "r", encoding="utf-8", errors="ignore") as file:
        text = file.read().strip()

    return [{
        "text": text,
        "page": 1,
        "source": os.path.basename(file_path),
    }]


def load_docx(file_path: str) -> list[dict]:
    doc = Document(file_path)
    paragraphs = []

    for para in doc.paragraphs:
        text = para.text.strip()

        if text:
            paragraphs.append(text)

    return [{
        "text": "\n".join(paragraphs),
        "page": 1,
        "source": os.path.basename(file_path),
    }]


def load_document(file_path: str) -> list[dict]:
    ext = os.path.splitext(file_path)[1].lower()

    if ext == ".pdf":
        return load_pdf(file_path)

    if ext == ".txt":
        return load_txt(file_path)

    if ext == ".docx":
        return load_docx(file_path)

    raise ValueError(f"Unsupported file type: {ext}")