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


def build_config(command_path: str | None) -> dict:
    if command_path:
        command = command_path
        args = []
    else:
        # fallback to current python -m module
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
                    "MCP_RUNS_ROOT": "runs",
                    "TMPDIR": "runs",
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
        help=(
            "Use octave-mcp console script if available"
        ),
    )
    args = p.parse_args()

    cmd_path = None
    if args.prefer_console_script:
        cmd_path = find_console_script("octave-mcp")
        if cmd_path:
            print(f"Found console script at: {cmd_path}")
        else:
            print("octave-mcp console script not found on PATH; falling back to Python -m module")
    else:
        # Try console script first, then fallback
        cmd_path = find_console_script("octave-mcp")

    cfg = build_config(cmd_path)
    out_path = Path(args.out)
    out_path.write_text(json.dumps(cfg, indent=2, ensure_ascii=False))
    print(f"Wrote {out_path.absolute()}")


if __name__ == "__main__":
    main()
