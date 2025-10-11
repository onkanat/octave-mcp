import os
import sys

from fastapi.testclient import TestClient

SRC_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../src"))
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from app import app  # noqa: E402


def test_grabcode_contract():
    from api import endpoints

    class DummyPublish:
        def __init__(self, share_id: str = "shareXYZ"):
            self.share_id = share_id

    async def fake_get_published_run(share_id: str):
        return {"publish": DummyPublish(share_id), "run": {"code": "x=1\nprint(x)"}, "images": []}

    endpoints.publish_service.get_published_run = (  # type: ignore[attr-defined]
        fake_get_published_run
    )

    client = TestClient(app)
    payload = {"share_id": "shareXYZ"}
    response = client.post("/api/v1/grabcode", json=payload)
    assert response.status_code == 200
    data = response.json()
    # Contract: code_b64, line_count, warnings[]
    assert "code_b64" in data
    assert "line_count" in data
    assert "warnings" in data
