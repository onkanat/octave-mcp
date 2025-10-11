from __future__ import annotations

import argparse
import logging
import os
import threading
from base64 import b64encode
from typing import Annotated, Any, Dict, List, Optional

from mcp.server.fastmcp import FastMCP

_LOG = logging.getLogger(__name__)

try:
    # When imported as a package (recommended): `import src.mcp_server`
    from .services.cleanup_service import CleanupService
    from .services.grabcode_service import GrabcodeService
    from .services.octave_runner import OctaveRunner
    from .services.publish_service import PublishService
    from .utils.config import get_env_int, get_env_str
    from .utils.resource_limits import ResourceLimiter
except Exception:
    # When executed as a script: `python src/mcp_server.py` (local dev)
    from services.cleanup_service import CleanupService  # type: ignore
    from services.grabcode_service import GrabcodeService  # type: ignore
    from services.octave_runner import OctaveRunner  # type: ignore
    from services.publish_service import PublishService  # type: ignore
    from utils.config import get_env_int, get_env_str  # type: ignore
    from utils.resource_limits import ResourceLimiter  # type: ignore

mcp = FastMCP("octave_mcp")

_octave_runner = OctaveRunner()
_publish_service = PublishService()
_grabcode_service = GrabcodeService()
_runs_root = get_env_str("MCP_RUNS_ROOT", None) or get_env_str("RUNS_ROOT", None) or "runs"
_retention_days = get_env_int("MCP_RUNS_RETENTION_DAYS", 0)
_cleanup_service = CleanupService(
    _runs_root,
    days=_retention_days if _retention_days > 0 else None,
)


@mcp.tool(
    name="octave_run",
    description=("Octave veya Python ile kod çalıştır; stdout/stderr ve " "görselleri döndürür."),
)
def tool_run(
    code: Annotated[str, "Çalıştırılacak Python/Octave kodu"],
    session_id: Annotated[Optional[str], "Oturum kimliği (opsiyonel)"] = None,
    images_b64: Annotated[bool, "Görselleri base64 olarak döndür (varsayılan: false)"] = False,
    max_image_bytes: Annotated[int, "Görsel başına maksimum byte (vars: 200000)"] = 200000,
) -> Dict[str, Any]:
    cpu_limit = get_env_int("MCP_CPU_LIMIT", 0) or None
    mem_mb = get_env_int("MCP_MEMORY_MB", 0) or None
    max_chars = get_env_int("MCP_MAX_OUTPUT_CHARS", 20000)
    timeout_s = get_env_int("MCP_TIMEOUT_SECONDS", 10)
    limits = ResourceLimiter(
        cpu_time_limit=cpu_limit,
        memory_limit_mb=mem_mb,
        max_output_chars=max_chars,
        max_image_size_bytes=0,
        timeout=timeout_s,
    )
    result = _octave_runner.run_code(code, limits, include_image_paths=True)

    # Base64 görüntü isteğe bağlı
    if images_b64 and result.get("images"):
        out_images: List[Dict[str, Any]] = []
        for img in result["images"]:
            name = img.get("name")
            path = img.get("path")
            data_b64 = None
            size = None
            try:
                if path and os.path.isfile(path):
                    size = os.path.getsize(path)
                    if size <= max_image_bytes:
                        with open(path, "rb") as f:
                            data_b64 = b64encode(f.read()).decode("ascii")
                # Path yoksa ya da limit aşıldıysa sadece isim bırak
            except Exception:
                pass
            entry: Dict[str, Any] = {"name": name}
            if path:
                entry["path"] = path
            if data_b64:
                entry["b64"] = data_b64
            if size is not None:
                entry["size"] = size
            out_images.append(entry)
        result["images"] = out_images
    return result


@mcp.tool(
    name="octave_publish",
    description="Kodu HTML'e dönüştürüp runs/<session_id>/published altına kaydeder.",
)
def tool_publish(
    code: Annotated[str, "Yayınlanacak kod"],
    session_id: Annotated[Optional[str], "Oturum kimliği (opsiyonel)"] = None,
) -> Dict[str, Any]:
    return _publish_service.publish(code, session_id)


@mcp.tool(name="octave_grabcode", description="Verilen oturum için son yayınlanan kodu getirir.")
def tool_grabcode(session_id: Annotated[str, "Oturum kimliği"]) -> Dict[str, Any]:
    return _grabcode_service.grab_code(session_id)


@mcp.tool(
    name="admin_cleanup",
    description=("Saklama ayarına göre eski runs klasörlerini temizler."),
)
def tool_cleanup(
    dry_run: Annotated[bool, "Sadece raporla, silme (varsayılan true)"] = True,
    force: Annotated[bool, "Yaş kontrolünü atla, hepsini hedefle (dikkat)"] = False,
    max_age_hours: Annotated[Optional[int], "Maksimum yaş (saat)"] = None,
    max_age_days: Annotated[Optional[int], "Maksimum yaş (gün)"] = None,
    session_id: Annotated[Optional[str], "Sadece bu oturumu hedefle"] = None,
) -> Dict[str, Any]:
    allow_force = os.environ.get("MCP_ALLOW_FORCE_DELETE", "false").lower() in ("1", "true", "yes")
    if force and not allow_force:
        return {
            "deleted_runs": 0,
            "deleted_sessions": 0,
            "dry_run": dry_run,
            "errors": [
                {
                    "path": None,
                    "error": (
                        "Force delete disabled by policy. "
                        "Set MCP_ALLOW_FORCE_DELETE=true to enable."
                    ),
                },
            ],
        }
    return _cleanup_service.cleanup(
        dry_run=dry_run,
        force=force,
        max_age_hours=max_age_hours,
        max_age_days=max_age_days,
        session_id=session_id,
    )


def main() -> None:
    """Entry point for MCP server console script."""
    parser = argparse.ArgumentParser(
        description="Run OctaveMCP servers (MCP STDIO and optional HTTP API)"
    )
    parser.add_argument(
        "--no-http",
        action="store_true",
        help="Do not start HTTP API (only STDIO)",
    )
    parser.add_argument(
        "--http-host",
        default="127.0.0.1",
        help="HTTP API bind host",
    )
    parser.add_argument(
        "--http-port",
        type=int,
        default=8000,
        help="HTTP API bind port",
    )
    parser.add_argument(
        "--transport",
        default="stdio",
        choices=["stdio", "sse", "streamable-http"],
        help="FastMCP transport to run (default: stdio)",
    )
    args = parser.parse_args()

    try:
        _print_lmstudio_suggestions()
    except Exception:
        # Do not block server startup on suggestion printing errors
        pass

    http_thread = None
    if not args.no_http:
        http_thread = _start_http_api(host=args.http_host, port=args.http_port)

    # Run the MCP transport (blocking)
    mcp.run(transport=args.transport)

    # If HTTP server was started, join thread briefly to keep process alive until mcp.run exits
    if http_thread is not None and http_thread.is_alive():
        try:
            http_thread.join(0)
        except Exception:
            pass


def _start_http_api(host: str = "127.0.0.1", port: int = 8000) -> threading.Thread | None:
    """Start the FastAPI HTTP endpoints in a background thread using uvicorn.

    Returns the Thread if started, otherwise None (uvicorn not available).
    """
    # Ensure repo root is on sys.path so imports like `src.api.endpoints` work
    try:
        import sys
        from pathlib import Path

        repo_root = Path.cwd().resolve()
        if str(repo_root) not in sys.path:
            sys.path.insert(0, str(repo_root))
    except Exception:
        pass

    # FastAPI app will be imported by uvicorn when running subprocess

    import subprocess
    import sys

    def run_server() -> None:
        try:
            cmd = [
                sys.executable,
                "-m",
                "uvicorn",
                "src.api.endpoints:app",
                "--host",
                host,
                "--port",
                str(port),
            ]
            _LOG.info("Starting uvicorn subprocess: %s", " ".join(cmd))
            proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            # Attach proc to thread for potential inspection
            try:
                threading.current_thread().proc = proc  # type: ignore[attr-defined]
            except Exception:
                pass
            # Stream subprocess output to our logger
            if proc.stdout is not None:
                for line in iter(proc.stdout.readline, b""):
                    try:
                        _LOG.info(line.decode("utf-8", errors="replace").rstrip())
                    except Exception:
                        pass
            proc.wait()
        except Exception:
            _LOG.exception("HTTP server failed")

    thread = threading.Thread(target=run_server, daemon=True)
    thread.start()
    return thread


def _print_lmstudio_suggestions() -> None:
    """Print two LM Studio mcp JSON suggestions:
    1) Portable: use the console-script name `octave-mcp` (works for pip installs)
    2) Absolute: full command using current python and repo src path (useful for local dev)
    This function is non-invasive: it only prints to stdout and does not change behavior.
    """
    import json
    from pathlib import Path

    repo_root = Path.cwd().resolve()
    portable = {
        "mcpServers": {
            "octave_execute": {
                "command": "octave-mcp",
                "args": [],
                "env": {"MCP_RUNS_ROOT": "runs"},
            }
        }
    }

    import sys

    absolute = {
        "mcpServers": {
            "octave_execute": {
                "command": sys.executable,
                "args": [str(repo_root / "src" / "mcp_server.py")],
                "env": {"MCP_RUNS_ROOT": str(repo_root / "runs")},
            }
        }
    }

    print(
        "\n=== LM Studio MCP suggestions (copy-paste into LM Studio or encode as deeplink) ===\n"
    )
    print("--- Portable (use if you've installed octave-mcp via pip) ---")
    print(json.dumps(portable, indent=2, ensure_ascii=False))
    print("\n--- Absolute (use for local dev / if LM Studio cannot find console-script) ---")
    print(json.dumps(absolute, indent=2, ensure_ascii=False))
    print("\n=================================================================\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Run OctaveMCP servers (MCP STDIO and optional HTTP API)"
    )
    parser.add_argument(
        "--no-http",
        action="store_true",
        help="Do not start HTTP API (only STDIO)",
    )
    parser.add_argument(
        "--http-host",
        default="127.0.0.1",
        help="HTTP API bind host",
    )
    parser.add_argument(
        "--http-port",
        type=int,
        default=8000,
        help="HTTP API bind port",
    )
    parser.add_argument(
        "--transport",
        default="stdio",
        choices=["stdio", "sse", "streamable-http"],
        help="FastMCP transport to run (default: stdio)",
    )
    args = parser.parse_args()

    try:
        _print_lmstudio_suggestions()
    except Exception:
        # Do not block server startup on suggestion printing errors
        pass

    http_thread = None
    if not args.no_http:
        http_thread = _start_http_api(host=args.http_host, port=args.http_port)

    # Run the MCP transport (blocking)
    mcp.run(transport=args.transport)

    # If HTTP server was started, join thread briefly to keep process alive until mcp.run exits
    if http_thread is not None and http_thread.is_alive():
        try:
            http_thread.join(0)
        except Exception:
            pass
