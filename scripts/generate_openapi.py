"""
Generate OpenAPI JSON from FastAPI app and write to artifacts/openapi.json.
"""
import json
import os
import sys
from pathlib import Path


def main() -> None:
    # Ensure 'src' on sys.path so `from app import app` works in CI
    repo_root = Path(__file__).resolve().parent.parent
    src_dir = repo_root / "src"
    if str(src_dir) not in sys.path:
        sys.path.insert(0, str(src_dir))

    from app import app  # type: ignore

    openapi = app.openapi()
    out_dir = repo_root / "artifacts"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / "openapi.json"
    with out_file.open("w", encoding="utf-8") as f:
        json.dump(openapi, f, ensure_ascii=False, indent=2)
    print(f"OpenAPI schema written to: {out_file}")


if __name__ == "__main__":
    main()
