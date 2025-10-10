from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
import time


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, max_requests=10, window_seconds=60):
        super().__init__(app)
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.clients = {}
        self._last_cleanup_window = None

    async def dispatch(self, request: Request, call_next):
        # Gerçek istemci IP'sini tespit etmeye çalış (proxy ardında olabilir)
        # Öncelik: X-Forwarded-For (ilk IP), X-Real-IP; yoksa request.client.host
        xff = request.headers.get("x-forwarded-for")
        if xff:
            client_ip = xff.split(",")[0].strip()
        else:
            xri = request.headers.get("x-real-ip")
            client_ip = (
                xri.strip() if xri else (request.client.host if request.client else "unknown")
            )
        now = time.time()
        window = int(now // self.window_seconds)
        # Eski pencere anahtarlarını periyodik temizle (basit, global)
        if self._last_cleanup_window is None or window != self._last_cleanup_window:
            try:
                keys_to_delete = [k for k in self.clients.keys() if k[1] < window - 1]
                for k in keys_to_delete:
                    self.clients.pop(k, None)
            except Exception:
                pass
            self._last_cleanup_window = window
        key = (client_ip, window)
        self.clients.setdefault(key, 0)
        self.clients[key] += 1
        count = self.clients[key]
        remaining = max(self.max_requests - count, 0)
        reset_ts = int((window + 1) * self.window_seconds)
        reset_in = max(reset_ts - int(now), 0)
        if count > self.max_requests:
            from fastapi.responses import JSONResponse

            resp = JSONResponse(status_code=429, content={"error": "Rate limit exceeded"})
            resp.headers["Retry-After"] = str(reset_in)
            resp.headers["X-RateLimit-Limit"] = str(self.max_requests)
            resp.headers["X-RateLimit-Remaining"] = "0"
            resp.headers["X-RateLimit-Reset"] = str(reset_ts)
            return resp

        response = await call_next(request)
        # Başarı durumunda da bilgi başlıkları ekle
        try:
            response.headers["X-RateLimit-Limit"] = str(self.max_requests)
            response.headers["X-RateLimit-Remaining"] = str(remaining)
            response.headers["X-RateLimit-Reset"] = str(reset_ts)
        except Exception:
            pass
        return response


# TODO: Session persistence ve temizlik entegrasyonu ayrı servislerde uygulanacak.
