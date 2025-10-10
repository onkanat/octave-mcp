import os
import sys

from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))
from api.endpoints import app  # noqa: E402


def test_smoke_octave():
    client = TestClient(app)
    code = "print('smoke-local')"
    session_id = "smoke_local_1"

    # Publish
    r_pub = client.post("/publish", json={"session_id": session_id, "code": code})
    assert r_pub.status_code == 200
    j_pub = r_pub.json()
    assert j_pub["html_b64"] and j_pub["html_name"]

    # Grabcode
    r_grab = client.post("/grabcode", json={"session_id": session_id})
    assert r_grab.status_code == 200
    j_grab = r_grab.json()
    assert j_grab["code"] == code

    # Run
    r_run = client.post("/run_octave", json={"session_id": session_id, "code": code})
    assert r_run.status_code == 200
    j_run = r_run.json()
    assert j_run["success"] is True
    assert "smoke-local" in j_run["stdout"]
