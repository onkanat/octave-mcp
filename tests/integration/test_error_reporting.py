from fastapi.testclient import TestClient
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))
from api.endpoints import app

def test_error_reporting_format():
    client = TestClient(app)
    # Söz dizimi hatalı kod gönder
    code = "print('A'"
    payload = {"code": code, "session_id": "err1"}
    response = client.post("/run_octave", json=payload)
    assert response.status_code == 200
    data = response.json()
    # Hata beklenmeli, stderr ve exit_code != 0 olmalı
    assert not data["success"]
    assert data["exit_code"] != 0
    assert data["stderr"] != ""
