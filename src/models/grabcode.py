from typing import List

class Grabcode:
    def __init__(self, code_b64: str, line_count: int, warnings: List[str]):
        self.code_b64 = code_b64
        self.line_count = line_count
        self.warnings = warnings or []
