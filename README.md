# VietMind-RAG

**VietMind-RAG** is a local Vietnamese Retrieval-Augmented Generation (RAG) assistant that allows users to upload documents and ask questions based on their own knowledge base.

The system supports PDF, TXT, and DOCX files, retrieves relevant document chunks using semantic search, and generates Vietnamese answers with a local LLM through Ollama.

## Features

* Upload PDF, TXT, and DOCX documents
* Extract and chunk document content
* Generate multilingual text embeddings
* Store and search document vectors with ChromaDB
* Retrieve relevant context for each user question
* Generate answers using a local Ollama LLM
* FastAPI backend with interactive API docs
* Streamlit web interface for document upload and chat
* Display retrieved sources for answer transparency

## Demo Flow

```text
Upload Document
      ↓
Text Extraction
      ↓
Chunking
      ↓
Embedding
      ↓
ChromaDB Vector Store
      ↓
User Question
      ↓
Semantic Retrieval
      ↓
Ollama LLM
      ↓
Vietnamese Answer + Retrieved Sources
```

## Tech Stack

| Component        | Technology                     |
| ---------------- | ------------------------------ |
| Backend          | FastAPI                        |
| Frontend         | Streamlit                      |
| Vector Database  | ChromaDB                       |
| Embedding Model  | Sentence Transformers          |
| Local LLM        | Ollama-compatible local models |
| Document Parsing | PyMuPDF, python-docx           |
| Language         | Python                         |

## Project Structure

```text
vietmind-rag/
├── app/
│   ├── main.py
│   ├── document_loader.py
│   ├── chunker.py
│   ├── embedder.py
│   ├── vector_store.py
│   ├── llm_client.py
│   └── rag_pipeline.py
│
├── ui/
│   └── streamlit_app.py
│
├── data/
│   ├── uploads/
│   └── chroma_db/
│
├── requirements.txt
├── README.md
└── .gitignore
```

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/Xenko2005/Vietmind-RAG.git
cd Vietmind-RAG
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate the environment on Windows:

```bash
.venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Install and run Ollama

This project uses Ollama to run a local LLM.
By default, the project is configured to use `qwen3:4b`, but you can replace it with another local model depending on your machine's hardware.

Recommended local models:

| Model         | Notes                                        |
| ------------- | -------------------------------------------- |
| `qwen3:1.7b`  | Lightweight option for low-resource machines |
| `qwen3:4b`    | Default model, balanced for local RAG        |
| `llama3.2:3b` | Lightweight general-purpose model            |
| `gemma3:4b`   | Good small model for local usage             |
| `mistral:7b`  | Stronger model, but requires more resources  |
| `qwen3:8b`    | Better reasoning quality, but heavier        |

Pull the default model:

```bash
ollama pull qwen3:4b
```

Make sure Ollama is running:

```bash
ollama serve
```

If Ollama is already running in the background, this step can be skipped.

To use another model, pull it with Ollama and update the model name in:

```text
app/llm_client.py
```

Example:

```python
model: str = "qwen3:4b"
```

Change it to another model, such as:

```python
model: str = "llama3.2:3b"
```

## How to Run

### 1. Start FastAPI backend

```bash
uvicorn app.main:app --reload
```

Open the API documentation:

```text
http://localhost:8000/docs
```

### 2. Start Streamlit frontend

Open a new terminal and run:

```bash
python -m streamlit run ui/streamlit_app.py
```

Open the web app:

```text
http://localhost:8501
```

## How to Use

1. Start the FastAPI backend.
2. Start the Streamlit frontend.
3. Upload a PDF, TXT, or DOCX document.
4. Wait for the document to be indexed.
5. Ask questions in Vietnamese.
6. View the answer and retrieved document sources.

Example questions:

```text
Tài liệu này nói về nội dung gì?
```

```text
Hãy tóm tắt các ý chính trong tài liệu.
```

```text
Phương pháp được đề cập trong tài liệu là gì?
```

## Current Version

**Version:** `v0.1.0`

This is the first MVP version of VietMind-RAG. It includes document upload, text chunking, vector storage, semantic retrieval, local LLM answering, FastAPI backend, and Streamlit UI.

## Roadmap

* [ ] Improve citation formatting
* [ ] Add document management features
* [ ] Prevent duplicate indexing
* [ ] Add retrieval evaluation metrics
* [ ] Add hybrid search with BM25 and vector search
* [ ] Add reranking for better retrieval quality
* [ ] Add Docker support
* [ ] Add demo screenshots and video

## Author

Developed by **Xenko2005** as a personal AI/NLP portfolio project.
