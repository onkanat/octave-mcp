class ImageResult:
    def __init__(self, name: str, mime: str, b64: str, size: int):
        self.name = name
        self.mime = mime
        self.b64 = b64
        self.size = size
