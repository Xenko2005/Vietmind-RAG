\# VietMind-RAG



VietMind-RAG is a local Vietnamese Retrieval-Augmented Generation assistant.  

It allows users to upload documents such as PDF, TXT, or DOCX files and ask questions in Vietnamese based on the uploaded content.



\## Features



\- Upload PDF, TXT, and DOCX documents

\- Parse and chunk document content

\- Generate multilingual embeddings

\- Store vectors using ChromaDB

\- Retrieve relevant document chunks

\- Generate answers using a local Ollama LLM

\- FastAPI backend

\- Streamlit chat interface



\## Tech Stack



\- Python

\- FastAPI

\- Streamlit

\- ChromaDB

\- Sentence Transformers

\- Ollama

\- Qwen3



\## Project Structure



```text

vietmind-rag/

├── app/

│   ├── main.py

│   ├── document\_loader.py

│   ├── chunker.py

│   ├── embedder.py

│   ├── vector\_store.py

│   ├── llm\_client.py

│   └── rag\_pipeline.py

├── ui/

│   └── streamlit\_app.py

├── data/

│   ├── uploads/

│   └── chroma\_db/

├── requirements.txt

├── README.md

└── .gitignore



How to Run

1\. Create virtual environment

python -m venv .venv

.venv\\Scripts\\activate

2\. Install dependencies

pip install -r requirements.txt

3\. Pull Ollama model

ollama pull qwen3:4b

4\. Run FastAPI backend

uvicorn app.main:app --reload



Backend docs:



http://localhost:8000/docs

5\. Run Streamlit frontend

python -m streamlit run ui/streamlit\_app.py



Frontend:



http://localhost:8501

Current Version



Version: v0.1.0



This is the first MVP version of VietMind-RAG.





\---



\# 4. Push lên GitHub



Trong thư mục project, chạy:



```bat

git init

git add .

git commit -m "Initial commit: VietMind-RAG MVP v0.1.0"

