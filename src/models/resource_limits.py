class ResourceLimits:
    def __init__(self, cpu_time_limit: int, memory_limit_mb: int, max_output_chars: int, max_image_size_bytes: int, timeout: int):
        self.cpu_time_limit = cpu_time_limit
        self.memory_limit_mb = memory_limit_mb
        self.max_output_chars = max_output_chars
        self.max_image_size_bytes = max_image_size_bytes
        self.timeout = timeout
