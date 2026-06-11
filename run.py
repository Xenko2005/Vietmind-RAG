import subprocess
import sys
import os


ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
PYTHON = sys.executable


def main():
    command = [
        PYTHON,
        "-m",
        "uvicorn",
        "app.main:app",
        "--reload",
        "--host",
        "127.0.0.1",
        "--port",
        "8000",
    ]

    print("Starting VietMind-RAG...")
    print("Frontend: http://127.0.0.1:8000")
    print("API docs: http://127.0.0.1:8000/docs")
    print("Press CTRL + C to stop.\n")

    subprocess.run(command, cwd=ROOT_DIR)


if __name__ == "__main__":
    main()