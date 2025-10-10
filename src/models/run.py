from typing import List, Optional
from .image_result import ImageResult
from .resource_limits import ResourceLimits

class Run:
    def __init__(self, code: str, stdout: str, stderr: str, exit_code: int, runtime_seconds: float, images: Optional[List[ImageResult]], resource_limits: ResourceLimits):
        self.code = code
        self.stdout = stdout
        self.stderr = stderr
        self.exit_code = exit_code
        self.runtime_seconds = runtime_seconds
        self.images = images or []
        self.resource_limits = resource_limits
