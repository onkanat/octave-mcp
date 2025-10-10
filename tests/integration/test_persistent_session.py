from fastapi.testclient import TestClient
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../src")))
from api.endpoints import app


def test_persistent_session_flow():
    client = TestClient(app)
    session_id = "sess1"
    payload1 = {"code": "print('A')", "session_id": session_id}
    payload2 = {"code": "print('B')", "session_id": session_id}
    r1 = client.post("/run_octave", json=payload1)
    r2 = client.post("/run_octave", json=payload2)
    assert r1.status_code == 200
    assert r2.status_code == 200
    # Dummy: session_id ile iki çağrı da başarılı olmalı (gerçek session koruması ileride)
    assert r1.json()["success"]
    assert r2.json()["success"]
