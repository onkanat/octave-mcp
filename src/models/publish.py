from typing import List, Optional

from .image_result import ImageResult


class Publish:
    def __init__(
        self,
        html_b64: str,
        html_truncated: bool,
        html_original_size: int,
        publish_dir: str,
        html_name: str,
        images: Optional[List[ImageResult]],
        warnings: Optional[List[str]],
    ):
        self.html_b64 = html_b64
        self.html_truncated = html_truncated
        self.html_original_size = html_original_size
        self.publish_dir = publish_dir
        self.html_name = html_name
        self.images = images or []
        self.warnings = warnings or []
