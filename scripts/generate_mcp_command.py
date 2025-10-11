#!/usr/bin/env python3
"""Generate a portable or absolute-path `mcp_command.json` for LM Studio.

Behavior:
- If a console script `octave-mcp` is on PATH, produce a JSON that uses it as `command`.
- Otherwise try to resolve `python -m octave_mcp.mcp_server` using the current Python executable.
- Write output to `mcp_command.generated.json` in the repo root.

Usage:
  python3 scripts/generate_mcp_command.py --out mcp_command.generated.json

This helper is intended to be run by users after `pip install octave-mcp` so the produced
JSON contains runnable absolute paths LM Studio can execute.
"""
import argparse
import json
import shutil
import sys
from pathlib import Path


DEFAULT_OUT = "mcp_command.generated.json"


def find_console_script(cmd_name: str) -> str | None:
    path = shutil.which(cmd_name)
    return path


def wrapper_imports_src(wrapper_path: str) -> bool:
    """Return True if the console-script wrapper appears to import from 'src' (broken layout).

    We read the file and look for common patterns like 'from src.' or 'import src'.
    """
    try:
        p = Path(wrapper_path)
        if not p.is_file():
            return False
        txt = p.read_text(errors="ignore")
        for token in ("from src.", "import src", "from src.mcp_server", "src.mcp_server"):
            if token in txt:
                return True
    except Exception:
        return False
    return False


def build_config(command_path: str | None) -> dict:
    repo_root = Path.cwd().resolve()
    local_server = repo_root / "src" / "mcp_server.py"

    if command_path:
        command = command_path
        args = []
    elif local_server.exists():
        # prefer running the local checkout's server script in dev mode
        command = sys.executable
        args = [str(local_server)]
    else:
        # fallback to python -m module (for installed packages)
        command = sys.executable
        args = ["-m", "octave_mcp.mcp_server"]

    cfg = {
        "mcpServers": {
            "octave_execute": {
                "command": command,
                "args": args,
                "env": {
                    "PYTHONUNBUFFERED": "1",
                    "PATH": "/opt/homebrew/bin:/usr/local/bin:${PATH}",
                    "MCP_RUNS_ROOT": str((repo_root / "runs")),
                    "TMPDIR": str((repo_root / "runs")),
                    "OCTAVE_RUNNER_MODE": "octave",
                    "MCP_IS_VISION_MODEL": "false",
                    "MCP_RATE_LIMIT_MAX": "100",
                    "MCP_RATE_LIMIT_WINDOW": "60",
                    "MCP_MAX_OUTPUT_CHARS": "20000",
                    "MCP_TIMEOUT_SECONDS": "10",
                    "MCP_CPU_LIMIT": "0",
                    "MCP_MEMORY_MB": "0",
                    "MCP_RUNS_RETENTION_DAYS": "0",
                    "MCP_ALLOW_FORCE_DELETE": "true",
                },
            }
        }
    }
    return cfg


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--out", default=DEFAULT_OUT, help="Output JSON filename")
    p.add_argument(
        "--prefer-console-script",
        action="store_true",
        help=("Use octave-mcp console script if available"),
    )
    args = p.parse_args()

    cmd_path = find_console_script("octave-mcp")
    if cmd_path:
        # detect broken console-script wrappers that import from `src`
        # (these won't work when installed into other environments)
        if wrapper_imports_src(cmd_path):
            print(
                (
                    f"Console script at {cmd_path} appears to import from 'src'. "
                    "Using python -m fallback."
                )
            )
            cmd_path = None
        else:
            print(f"Found console script at: {cmd_path}")
    else:
        if args.prefer_console_script:
            print("octave-mcp console script not found on PATH; falling back to Python -m module")

    cfg = build_config(cmd_path)
    out_path = Path(args.out)
    out_path.write_text(json.dumps(cfg, indent=2, ensure_ascii=False))
    print(f"Wrote {out_path.absolute()}")


if __name__ == "__main__":
    main()
