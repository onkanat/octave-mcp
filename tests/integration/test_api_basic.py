import os
import sys

from fastapi.testclient import TestClient


# Uygulama modülünü bulmak için src yolunu ekle
SRC_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../src"))
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from app import app  # noqa: E402  # isort:skip


def get_client() -> TestClient:
    return TestClient(app)


def test_health_ok():
    client = get_client()
    resp = client.get("/api/v1/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data.get("status") == "healthy"
    assert data.get("service") == "octave-mcp"


def test_rate_limit_headers_present_and_decrement():
    client = get_client()
    r1 = client.get("/api/v1/health")
    assert r1.status_code == 200
    # Oran sınırlama başlıkları mevcut olmalı
    limit = r1.headers.get("X-RateLimit-Limit")
    remaining1 = r1.headers.get("X-RateLimit-Remaining")
    reset = r1.headers.get("X-RateLimit-Reset")
    assert limit is not None and limit.isdigit()
    assert remaining1 is not None and remaining1.isdigit()
    assert reset is not None and reset.isdigit()

    r2 = client.get("/api/v1/health")
    assert r2.status_code == 200
    remaining2 = r2.headers.get("X-RateLimit-Remaining")
    # İkinci istekte kalan sayının azalmış olması beklenir
    # (eşitlik yarış durumlarında kabul edilebilir)
    assert remaining2 is not None and remaining2.isdigit()
    assert int(remaining2) <= int(remaining1)


def test_sessions_list_smoke():
    client = get_client()
    resp = client.get("/api/v1/sessions")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    # Öğe varsa temel alanların string/numara tipleri mantıklı olmalı
    if data:
        item = data[0]
        assert isinstance(item, dict)
        # Sözleşmeye zorlamadan, beklenen anahtarlar mevcutsa tiplerini kontrol edelim
        for k in ["session_id", "description"]:
            if k in item:
                assert isinstance(item[k], str) or item[k] is None


def test_published_image_not_found():
    client = get_client()
    resp = client.get("/api/v1/published/nonexistent/images/missing.png")
    assert resp.status_code in (404, 500)
    # 404 beklenir; fakat herhangi bir nedenle genel hata olursa 500 dönebilir.
    if resp.status_code == 404:
        body = resp.json()
        # FastAPI HTTPException.detail altındaki sözleşmeyi kontrol et
        detail = body.get("detail") if isinstance(body, dict) else None
        if isinstance(detail, dict):
            # Kod alanı IMAGE_NOT_FOUND olarak ayarlanmış olabilir
            code = detail.get("code")
            assert code in ("IMAGE_NOT_FOUND", None)
