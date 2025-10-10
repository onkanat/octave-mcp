import os
import sys

from fastapi.testclient import TestClient

from api.endpoints import app

sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../../src")))


def test_run_octave_includes_error_block_on_failure():
    client = TestClient(app)
    # Söz dizimi hatalı kod
    payload = {"code": "print('A'", "session_id": "e1"}
    res = client.post("/run_octave", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is False
    assert data["exit_code"] != 0
    # Ek alanlar (sözleşmeyi bozmaz)
    assert "error" in data
    err = data["error"]
    # Minimum alanlar
    for key in ("id", "type", "message", "timestamp"):
        assert key in err
