import os

from fastapi import FastAPI
from pydantic import BaseModel

from api.middleware import RateLimitMiddleware
from services.cleanup_service import CleanupService
from services.grabcode_service import GrabcodeService
from services.octave_runner import OctaveRunner
from services.publish_service import PublishService
from utils.config import get_env_int, get_env_str
from utils.error_format import build_error_block
from utils.resource_limits import ResourceLimiter
from utils.vectorization import analyze_vectorization

app = FastAPI()
# Rate limit ayarlarını .env'den oku (varsayılan: 100 istek / 60 sn)
_max_requests = get_env_int("MCP_RATE_LIMIT_MAX", 100)
_window_seconds = get_env_int("MCP_RATE_LIMIT_WINDOW", 60)
app.add_middleware(
    RateLimitMiddleware,
    max_requests=_max_requests,
    window_seconds=_window_seconds)
_octave_runner = OctaveRunner()
_publish_service = PublishService()
_grabcode_service = GrabcodeService()
_runs_root = get_env_str(
    "MCP_RUNS_ROOT",
    os.path.abspath("runs")) or os.path.abspath("runs")
_retention_days = get_env_int("MCP_RUNS_RETENTION_DAYS", 0)
_cleanup_service = CleanupService(_runs_root,
                                  days=_retention_days if _retention_days > 0 else None)

# Basit in-memory session -> kod haritası
session_code_store = {}


# --- Request/Response Models (Stub) ---
class RunRequest(BaseModel):
    code: str
    session_id: str | None = None


class PublishRequest(BaseModel):
    code: str
    session_id: str | None = None


class GrabcodeRequest(BaseModel):
    session_id: str


# --- Endpoints (Stub) ---
@app.post("/run_octave")
def run_octave(req: RunRequest):
    code = req.code
    # Kaynak limitlerini .env'den oku, güvenli varsayılanlar uygula
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
    result = _octave_runner.run_code(code, limits)

    # Bilgilendirici vektörizasyon uyarıları (sadece ek alan, sözleşmeyi bozmaz)
    try:
        vec_warn = analyze_vectorization(code)
        if isinstance(result, dict):
            result["vectorization_warnings"] = vec_warn
    except Exception:
        pass

    # Başarısızlıkta standart hata bloğu ekle (sözleşmeye ek alan)
    try:
        if isinstance(result, dict) and not result.get("success", False):
            stderr = result.get("stderr", "") or ""
            stdout = result.get("stdout", "") or ""
            err_type = "timeout" if "TimeoutExpired" in stderr else "runtime_error"
            result["error"] = build_error_block(
                type=err_type,
                message=stderr.strip() or "Execution failed",
                session_id=req.session_id,
                run_id=None,
                stdout_truncated=("...[truncated]" in stdout),
                stderr_truncated=("...[truncated]" in stderr),
                resource_violation=None,
                details={"exit_code": result.get("exit_code")},
            )
    except Exception:
        pass

    return result


@app.post("/publish")
def publish(req: PublishRequest):
    # Koddan dummy HTML üret, base64 ile encode et
    return _publish_service.publish(req.code, req.session_id)


@app.post("/grabcode")
def grabcode(req: GrabcodeRequest):
    return _grabcode_service.grab_code(req.session_id)


class CleanupRequest(BaseModel):
    dry_run: bool = True
    force: bool = False
    max_age_hours: int | None = None
    max_age_days: int | None = None
    session_id: str | None = None


@app.post("/admin/cleanup")
def admin_cleanup(req: CleanupRequest):
    allow_force = os.environ.get(
        "MCP_ALLOW_FORCE_DELETE",
        "false").lower() in (
        "1",
        "true",
        "yes")
    if req.force and not allow_force:
        return {
            "deleted_runs": 0,
            "deleted_sessions": 0,
            "dry_run": req.dry_run,
            "errors": [
                {
                    "path": None,
                    "error": "Force delete disabled by policy. Set MCP_ALLOW_FORCE_DELETE=true to enable.",
                }
            ],
        }
    return _cleanup_service.cleanup(
        dry_run=req.dry_run,
        force=req.force,
        max_age_hours=req.max_age_hours,
        max_age_days=req.max_age_days,
        session_id=req.session_id,
    )
