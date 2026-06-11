import os
import shutil
from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel

from app.document_loader import load_document
from app.chunker import chunk_text
from app.vector_store import VectorStore
from app.rag_pipeline import RAGPipeline


UPLOAD_DIR = "data/uploads"

app = FastAPI(
    title="VietMind-RAG API",
    description="Local Vietnamese RAG Assistant",
    version="0.1.0"
)


class AskRequest(BaseModel):
    question: str
    top_k: int = 5


@app.get("/")
def root():
    return {
        "message": "VietMind-RAG API is running."
    }


@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    os.makedirs(UPLOAD_DIR, exist_ok=True)

    file_path = os.path.join(UPLOAD_DIR, file.filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    pages = load_document(file_path)
    chunks = chunk_text(pages)

    vector_store = VectorStore()
    num_chunks = vector_store.add_chunks(chunks)

    return {
        "filename": file.filename,
        "num_pages_or_sections": len(pages),
        "num_chunks": num_chunks,
        "message": "File uploaded and indexed successfully."
    }


@app.post("/ask")
def ask_question(request: AskRequest):
    rag = RAGPipeline()
    result = rag.ask(
        question=request.question,
        top_k=request.top_k
    )

    return result