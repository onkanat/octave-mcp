from fastapi.testclient import TestClient
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../src")))
from api.endpoints import app


def test_resource_limit_enforcement():
    client = TestClient(app)
    # Sonsuz döngü ile timeout tetiklenmeli
    code = "while True:\n    pass"
    payload = {"code": code, "session_id": "rlim1"}
    response = client.post("/run_octave", json=payload)
    assert response.status_code == 200
    data = response.json()
    # Başarı beklenmemeli, timeout veya limit nedeniyle başarısız olmalı
    assert not data["success"]
    assert data["exit_code"] != 0
