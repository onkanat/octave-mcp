from __future__ import annotations

import time
import uuid
from typing import Any, Optional


def build_error_block(
    *,
    type: str,
    message: str,
    hint: Optional[str] = None,
    session_id: Optional[str] = None,
    run_id: Optional[str] = None,
    stdout_truncated: Optional[bool] = None,
    stderr_truncated: Optional[bool] = None,
    resource_violation: Optional[dict] = None,
    details: Optional[dict] = None,
) -> dict[str, Any]:
    """Standart hata bloğu sözlüğünü üretir.

    Bu yardımcı mevcut çağrıları bozmaz; çağrılmadığı sürece mevcut davranış değişmez.
    """
    return {
        "id": str(uuid.uuid4()),
        "type": type,
        "message": message,
        "hint": hint,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "session_id": session_id,
        "run_id": run_id,
        "stdout_truncated": stdout_truncated,
        "stderr_truncated": stderr_truncated,
        "resource_violation": resource_violation,
        "details": details or {},
    }


class ErrorFormatter:
    @staticmethod
    def format_error(identifier: str, message: str, stack: str, hint: str) -> dict:
        return {
            "identifier": identifier,
            "message": message,
            "stack": stack,
            "hint": hint
        }
