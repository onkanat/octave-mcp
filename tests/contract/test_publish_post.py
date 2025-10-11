import os
import sys

from fastapi.testclient import TestClient

SRC_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../src"))
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from app import app  # noqa: E402


def test_publish_contract():
    from api import endpoints

    async def fake_execute_code(*args, **kwargs):
        class DummyRun:
            def __init__(self):
                self.run_id = "rpub"
                self.session_id = kwargs.get("session_id")
                self.stdout = "pub"
                self.stderr = ""
                self.exit_code = 0
                self.runtime_seconds = 0.01
                self.images = []

            @property
            def success(self):
                return True

        return DummyRun()

    class DummyPublish:
        def __init__(self, share_id: str = "sharePUB12345678"):
            self.share_id = share_id

    async def fake_publish_run(*args, **kwargs):
        return DummyPublish()

    endpoints.octave_service.execute_code = fake_execute_code  # type: ignore[attr-defined]
    endpoints.publish_service.publish_run = fake_publish_run  # type: ignore[attr-defined]

    client = TestClient(app)
    payload = {"code": "print('publish test')", "session_id": "pubsess1"}
    response = client.post("/api/v1/publish", json=payload)
    assert response.status_code == 200
    data = response.json()
    # Contract: html_b64, html_truncated, html_original_size, publish_dir,
    # html_name, images[], warnings[]
    assert "html_b64" in data
    assert "html_truncated" in data
    assert "html_original_size" in data
    assert "publish_dir" in data
    assert "html_name" in data
    assert "images" in data
    assert "warnings" in data
