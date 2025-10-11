"""
Generate HTML API docs for src/ using pdoc and write to artifacts/docs.
"""
from pathlib import Path
import sys
import subprocess


def main() -> None:
    repo_root = Path(__file__).resolve().parent.parent
    out_dir = repo_root / "artifacts" / "docs"
    out_dir.mkdir(parents=True, exist_ok=True)
    # Ensure pdoc is available in dev deps; fallback install if missing
    try:
        __import__("pdoc")
    except Exception:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pdoc"])
    subprocess.check_call([sys.executable, "-m", "pdoc", "-o", str(out_dir), "src"])
    print(f"Docs written to: {out_dir}")


if __name__ == "__main__":
    main()
