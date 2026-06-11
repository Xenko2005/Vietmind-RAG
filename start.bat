@echo off
cd /d "%~dp0"

echo Starting VietMind-RAG...
echo Project path: %cd%

call .venv\Scripts\activate

python run.py

pause