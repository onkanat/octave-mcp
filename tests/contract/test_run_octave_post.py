from api.endpoints import app
import os
import sys

from fastapi.testclient import TestClient

sys.path.insert(
    0,
    os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            "../../src")))


def test_run_octave_contract():
    client = TestClient(app)
    payload = {"code": "disp(1+1);", "session_id": "testsession"}
    response = client.post("/run_octave", json=payload)
    assert response.status_code == 200
    data = response.json()
    # Contract: success, stdout, stderr, exit_code, runtime_seconds, images[]
    assert "success" in data
    assert "stdout" in data
    assert "stderr" in data
    assert "exit_code" in data
    assert "runtime_seconds" in data
    assert "images" in data
