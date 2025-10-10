from base64 import b64encode
from typing import Dict

from .store import session_code_store


class GrabcodeService:
    def grab_code(self, session_id: str) -> Dict:
        code = session_code_store.get(session_id, "")
        code_b64 = b64encode(code.encode("utf-8")).decode("utf-8")
        line_count = code.count("\n") + 1 if code else 0
        return {
            "code": code,
            "code_b64": code_b64,
            "line_count": line_count,
            "warnings": [],
        }
