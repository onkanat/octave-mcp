import os
import sys

from fastapi.testclient import TestClient

from api.endpoints import app

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../src")))


def test_smoke():
    client = TestClient(app)
    # Basit bir kodu publish et, grabcode ile geri al, run_octave ile çalıştır
    code = "print('smoke')"
    session_id = "smoke1"
    # Publish
    resp_pub = client.post("/publish", json={"session_id": session_id, "code": code})
    assert resp_pub.status_code == 200
    # Grabcode
    resp_grab = client.post("/grabcode", json={"session_id": session_id})
    assert resp_grab.status_code == 200
    data_grab = resp_grab.json()
    assert data_grab["code"] == code
    # Run
    resp_run = client.post("/run_octave", json={"session_id": session_id, "code": code})
    assert resp_run.status_code == 200
    data_run = resp_run.json()
    assert data_run["success"]
    assert "smoke" in data_run["stdout"]
