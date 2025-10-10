class ResourceLimiter:
    def __init__(
        self, cpu_time_limit, memory_limit_mb, max_output_chars, max_image_size_bytes, timeout
    ):
        self.cpu_time_limit = cpu_time_limit
        self.memory_limit_mb = memory_limit_mb
        self.max_output_chars = max_output_chars
        self.max_image_size_bytes = max_image_size_bytes
        self.timeout = timeout

    def preexec_fn(self):
        try:
            import resource
        except Exception:
            return None

        limits_to_apply = []
        if self.cpu_time_limit:
            limits_to_apply.append(
                (getattr(resource, "RLIMIT_CPU", None), int(self.cpu_time_limit))
            )
        if self.memory_limit_mb:
            mem_bytes = int(self.memory_limit_mb) * 1024 * 1024
            # RLIMIT_AS genelde sanal bellek; RLIMIT_DATA bazı sistemlerde çalışır
            limits_to_apply.append((getattr(resource, "RLIMIT_AS", None), mem_bytes))
            limits_to_apply.append((getattr(resource, "RLIMIT_DATA", None), mem_bytes))

        limits_to_apply = [(k, v) for (k, v) in limits_to_apply if k is not None]
        if not limits_to_apply:
            return None

        def _apply():
            import resource as res

            for key, val in limits_to_apply:
                try:
                    res.setrlimit(key, (val, val))
                except Exception:
                    # Desteklenmeyen limitler sessizce yoksayılır
                    pass

        return _apply
