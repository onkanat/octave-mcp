import os
import sys
from typing import Any, Dict

from fastapi.testclient import TestClient


SRC_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../src"))
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from app import app  # noqa: E402


def get_client() -> TestClient:
    return TestClient(app)


class DummyRun:
    def __init__(self, run_id: str = "run_1", session_id: str | None = None):
        self.run_id = run_id
        self.session_id = session_id
        self.stdout = "ok"
        self.stderr = ""
        self.exit_code = 0
        self.runtime_seconds = 0.01
        self.images = []

    @property
    def success(self) -> bool:  # matches domain model property
        return self.exit_code == 0


class DummyPublish:
    def __init__(self, share_id: str = "share1234567890"):
        self.share_id = share_id


def test_run_success_monkeypatch(monkeypatch):
    # Patch OctaveService.execute_code to return DummyRun
    from api import endpoints

    async def fake_execute_code(*args, **kwargs):
        return DummyRun(run_id="run_X", session_id=kwargs.get("session_id"))

    monkeypatch.setattr(endpoints.octave_service, "execute_code", fake_execute_code)

    client = get_client()
    resp = client.post(
        "/api/v1/run",
        json={"code": "print('x')", "session_id": "sess1"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert data["exit_code"] == 0
    assert isinstance(data["runtime_seconds"], (int, float))


def test_publish_success_monkeypatch(monkeypatch):
    from api import endpoints

    async def fake_execute_code(*args, **kwargs):
        return DummyRun(run_id="run_P")

    async def fake_publish_run(*args, **kwargs):
        return DummyPublish(share_id="share_ABCDEF12")

    monkeypatch.setattr(endpoints.octave_service, "execute_code", fake_execute_code)
    monkeypatch.setattr(endpoints.publish_service, "publish_run", fake_publish_run)

    client = get_client()
    resp = client.post(
        "/api/v1/publish",
        json={"code": "print('pub')"},
    )
    assert resp.status_code == 200
    data = resp.json()
    # Beklenen PublishResponse alanları
    for key in [
        "html_b64",
        "html_truncated",
        "html_original_size",
        "publish_dir",
        "html_name",
        "images",
        "warnings",
    ]:
        assert key in data
    assert isinstance(data["html_b64"], str)


def test_grabcode_success_monkeypatch(monkeypatch):
    from api import endpoints

    async def fake_get_published_run(share_id: str) -> Dict[str, Any]:
        return {
            "publish": DummyPublish(share_id=share_id),
            "run": {"code": "a = 1\nprint(a)"},
            "images": [],
            "share_url": f"http://localhost/published/{share_id}",
        }

    monkeypatch.setattr(endpoints.publish_service, "get_published_run", fake_get_published_run)

    client = get_client()
    resp = client.post(
        "/api/v1/grabcode",
        json={"share_id": "shareZ"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "code_b64" in data and isinstance(data["code_b64"], str)
    assert data["line_count"] == 2
