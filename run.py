import sys
import subprocess
from pathlib import Path
from src.backend import WellsPipelineService

def run_cli_mode(force_reparse: bool = False):
    pipeline = WellsPipelineService()
    print("Menginisialisasi pipeline Wells RAG...")
    pipeline.initialize(force_reparse=force_reparse)
    print("Inisialisasi selesai.\n")

    test_queries = [
        "Dimana letak lokasi sumur ?",
        "Berapa Total NPT sumur ?",
        "Wireline run apa yang direncanakan ?",
        "Apa arti dari istilah BHA, NPT, dan MDT pada glosarium migas?",
        "Siapa presiden Amerika Serikat saat ini dan bagaimana cuaca di Jakarta hari ini?"
    ]

    for i, query in enumerate(test_queries, 1):
        print(f"[{i}] Pertanyaan: {query}")
        result = pipeline.ask(query)
        print("Jawaban AI:")
        print(result.answer)
        print("-" * 60)

def run_streamlit_app():
    app_path = Path(__file__).resolve().parent / "src" / "frontend" / "app.py"
    command = [
        sys.executable,
        "-m",
        "streamlit",
        "run",
        str(app_path),
        "--server.headless=true"
    ]
    subprocess.run(command)

def main():
    if "--cli" in sys.argv:
        force_reparse = "--reparse" in sys.argv
        run_cli_mode(force_reparse=force_reparse)
    else:
        run_streamlit_app()

if __name__ == "__main__":
    main()
