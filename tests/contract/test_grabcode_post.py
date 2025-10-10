from fastapi.testclient import TestClient
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../src")))
from api.endpoints import app


def test_grabcode_contract():
    client = TestClient(app)
    payload = {"session_id": "pubsess1", "html_relpath": "run_123/published/script_publish.html"}
    response = client.post("/grabcode", json=payload)
    assert response.status_code == 200
    data = response.json()
    # Contract: code_b64, line_count, warnings[]
    assert "code_b64" in data
    assert "line_count" in data
    assert "warnings" in data
