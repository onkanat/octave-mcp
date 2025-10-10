from fastapi.testclient import TestClient
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../src")))
from api.endpoints import app


def test_publish_contract():
    client = TestClient(app)
    payload = {"code": "disp('publish test');", "session_id": "pubsess1"}
    response = client.post("/publish", json=payload)
    assert response.status_code == 200
    data = response.json()
    # Contract: html_b64, html_truncated, html_original_size, publish_dir, html_name, images[], warnings[]
    assert "html_b64" in data
    assert "html_truncated" in data
    assert "html_original_size" in data
    assert "publish_dir" in data
    assert "html_name" in data
    assert "images" in data
    assert "warnings" in data
