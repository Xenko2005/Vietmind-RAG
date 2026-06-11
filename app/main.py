import os
import shutil
from pathlib import Path

import requests
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from app.document_loader import load_document
from app.chunker import chunk_text
from app.vector_store import VectorStore
from app.rag_pipeline import RAGPipeline


BASE_DIR = Path(__file__).resolve().parent.parent
UPLOAD_DIR = BASE_DIR / "data" / "uploads"
FRONTEND_DIR = BASE_DIR / "frontend"

OLLAMA_BASE_URL = os.getenv(
    "OLLAMA_BASE_URL",
    "http://localhost:11434",
)

DEFAULT_LLM_MODEL = os.getenv(
    "DEFAULT_LLM_MODEL",
    "qwen3:4b",
)


app = FastAPI(
    title="VietMind-RAG API",
    description="Local Vietnamese RAG Assistant",
    version="0.3.0",
)


app.mount(
    "/static",
    StaticFiles(directory=str(FRONTEND_DIR)),
    name="static",
)


class AskRequest(BaseModel):
    question: str
    top_k: int = 5
    model: str = DEFAULT_LLM_MODEL


class DeleteDocumentRequest(BaseModel):
    source: str


@app.get("/")
def serve_frontend():
    return FileResponse(str(FRONTEND_DIR / "index.html"))


@app.get("/api/health")
def health_check():
    return {
        "message": "VietMind-RAG API is running.",
        "version": "0.3.0",
    }


@app.get("/models")
def list_local_models():
    try:
        response = requests.get(
            f"{OLLAMA_BASE_URL}/api/tags",
            timeout=10,
        )

        response.raise_for_status()

        data = response.json()
        models = data.get("models", [])

        model_names = [
            model.get("name")
            for model in models
            if model.get("name")
        ]

        return {
            "default_model": DEFAULT_LLM_MODEL,
            "models": model_names,
        }

    except Exception as e:
        return {
            "default_model": DEFAULT_LLM_MODEL,
            "models": [DEFAULT_LLM_MODEL],
            "warning": f"Cannot connect to Ollama: {str(e)}",
        }


@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

    file_path = UPLOAD_DIR / file.filename

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    pages = load_document(str(file_path))
    chunks = chunk_text(pages)

    vector_store = VectorStore()

    num_chunks = vector_store.add_chunks(
        chunks,
        replace_existing=True,
    )

    return {
        "filename": file.filename,
        "num_pages_or_sections": len(pages),
        "num_chunks": num_chunks,
        "message": (
            "File uploaded and indexed successfully. "
            "Old chunks from the same file were replaced."
        ),
    }


@app.post("/ask")
def ask_question(request: AskRequest):
    rag = RAGPipeline(
        llm_model=request.model,
    )

    result = rag.ask(
        question=request.question,
        top_k=request.top_k,
    )

    result["model"] = request.model

    return result


@app.get("/documents")
def list_documents():
    vector_store = VectorStore()

    return {
        "total_chunks": vector_store.count_chunks(),
        "documents": vector_store.list_documents(),
    }


@app.delete("/documents")
def delete_document(request: DeleteDocumentRequest):
    vector_store = VectorStore()

    deleted_chunks = vector_store.delete_by_source(request.source)

    return {
        "source": request.source,
        "deleted_chunks": deleted_chunks,
        "message": "Document chunks deleted successfully.",
    }


@app.delete("/reset")
def reset_knowledge_base():
    vector_store = VectorStore()
    vector_store.reset()

    return {
        "message": "Knowledge base reset successfully.",
    }